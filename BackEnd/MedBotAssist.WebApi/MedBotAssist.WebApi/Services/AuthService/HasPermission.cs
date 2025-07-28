using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.AspNetCore.Mvc;

namespace MedBotAssist.WebApi.Services.AuthService
{
    [AttributeUsage(AttributeTargets.Method | AttributeTargets.Class, AllowMultiple = true)]
    public class HasPermissionAttribute : AuthorizeAttribute, IAuthorizationFilter
    {
        private readonly string _requiredPermission;

        /// <summary>
        /// Initializes a new instance of the <see cref="HasPermissionAttribute"/> class.
        /// </summary>
        /// <param name="permission">The required permission name.</param>
        public HasPermissionAttribute(string requiredPermission)
        {
            _requiredPermission = requiredPermission;
        }

        /// <summary>
        /// Called to check if the current user has the required permission.
        /// </summary>
        /// <param name="context">The authorization filter context.</param>
        public void OnAuthorization(AuthorizationFilterContext context)
        {
            var user = context.HttpContext.User;
            if (user?.Identity == null || !user.Identity.IsAuthenticated)
            {
                context.Result = new UnauthorizedResult();
                return;
            }

            var permissions = user.Claims
                .Where(c => c.Type == "permission")
                .Select(c => c.Value)
                .ToList();

            if (!permissions.Contains(_requiredPermission))
            {
                context.Result = new ForbidResult();
            }
        }
    }
}
