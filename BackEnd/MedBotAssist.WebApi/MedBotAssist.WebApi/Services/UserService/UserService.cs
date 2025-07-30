using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Utils;
using Microsoft.EntityFrameworkCore;

namespace MedBotAssist.WebApi.Services.UserService
{
    /// <summary>
    /// Service for user-related operations.
    /// </summary>
    /// <remarks>
    /// Provides methods to retrieve user information from the database.
    /// </remarks>
    public class UserService : IUserService
    {
        private readonly IMedBotAssistDbContext _context;

        /// <summary>
        /// Initializes a new instance of the <see cref="UserService"/> class.
        /// </summary>
        /// <param name="context">Database context for accessing user data.</param>
        public UserService(IMedBotAssistDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Retrieves a user by their username.
        /// </summary>
        /// <param name="userName">The username of the user to retrieve.</param>
        /// <returns>
        /// A <see cref="UserDto"/> representing the user, or null if not found.
        /// </returns>
        public async Task<UserDto> GetUserByName(string userName)
        {
            var user = await _context.Users
                .FirstOrDefaultAsync(u => u.UserName.Equals(userName));

            return UserMapper.ToDto(user);
        }
    }
}
