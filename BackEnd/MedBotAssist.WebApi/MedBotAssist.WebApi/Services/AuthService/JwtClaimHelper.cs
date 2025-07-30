using System.Security.Claims;

namespace MedBotAssist.WebApi.Services.AuthService
{
    public static class JwtClaimHelper
    {
        /// <summary>
        /// Gets the "username" claim value from the current user's claims principal.
        /// </summary>
        /// <param name="user">The claims principal (e.g., HttpContext.User).</param>
        /// <returns>The username claim value if present; otherwise, null.</returns>
        public static string? GetUsernameClaim(ClaimsPrincipal user, string claimName)
        {
            return user?.Claims.FirstOrDefault(c => c.Type == claimName)?.Value;
        }
    }
}
