using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;
using MedBotAssist.Persistance.Context;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace MedBotAssist.WebApi.Services.AuthService
{
    /// <summary>
    /// Service responsible for user authentication and JWT token generation.
    /// </summary>
    public class AuthService : IAuthService
    {
        private readonly IMedBotAssistDbContext _context;
        private readonly IConfiguration _config;

        /// <summary>
        /// Initializes a new instance of the <see cref="AuthService"/> class.
        /// </summary>
        /// <param name="context">Database context for MedBotAssist.</param>
        /// <param name="config">Application configuration for JWT settings.</param>
        public AuthService(IMedBotAssistDbContext context, IConfiguration config)
        {
            _context = context;
            _config = config;
        }

        /// <summary>
        /// Authenticates a user with the provided credentials.
        /// </summary>
        /// <param name="request">Object containing username and password.</param>
        /// <returns>
        /// A <see cref="LoginResponse"/> object with the JWT token if credentials are valid; otherwise, null.
        /// </returns>
        public async Task<LoginResponse> LoginAsync(LoginRequest request)
        {
            var user = await _context.Users
                .FirstOrDefaultAsync(u => u.UserName == request.UserName);

            if (user == null || !BCrypt.Net.BCrypt.Verify(request.Password, user.Password))
                return null;

            var token = await GenerateJwtToken(user);

            return new LoginResponse
            {
                UserName = user.UserName,
                Token = token
            };
        }


        /// <summary>
        /// Registers a new user and assigns the specified role.
        /// </summary>
        /// <param name="request">Object containing user registration details such as username, email, password, and role.</param>
        /// <returns>
        /// A string message indicating the result of the registration process.
        /// Throws an exception if the specified role does not exist.
        /// </returns>
        public async Task<string> RegisterAsync(RegisterRequest request)
        {
            var role = await _context.Roles.FirstOrDefaultAsync(r => r.RoleId == 1);

            var user = new User
            {
                UserName = request.UserName,
                Email = request.Email,
                Password = BCrypt.Net.BCrypt.HashPassword(request.Password),
                Role = role.RoleName,
                FullName = request.FullName
            };

            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            var userRole = new UserRole
            {
                UserId = user.UserId,
                RoleId = role.RoleId
            };

            _context.UserRoles.Add(userRole);

            await _context.SaveChangesAsync();

            var doctor = new Doctor()
            {
                DoctorId = 0,
                UserId = user.UserId,
                SpecialtyId = request.SpecialtyId,
                MedicalLicenseNumber = request.MedicalLicenseNumber
            };
            _context.Doctors.Add(doctor);
            await _context.SaveChangesAsync();

            return "User successfully registered and role assigned.";
        }

        /// <summary>
        /// Generates a JWT token for the specified user, including role and permissions claims.
        /// </summary>
        /// <param name="user">The user for whom to generate the token.</param>
        /// <returns>A JWT token string.</returns>
        private async Task<string> GenerateJwtToken(User user)
        {
            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_config["JwtSettings:Secret"]));
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

            var roleIds = await _context.UserRoles
                .Where(ur => ur.UserId == user.UserId)
                .Select(ur => ur.RoleId)
                .ToListAsync();

            var permissions = await _context.RolePermissions
                .Where(rp => roleIds.Contains(rp.RoleId))
                .Select(rp => rp.Permission.PermissionName)
                .Distinct()
                .ToListAsync();

            var claims = new List<Claim>
                {
                    new Claim(JwtRegisteredClaimNames.Sub, user.UserId.ToString()),
                    new Claim("name", user.UserName),
                    new Claim("role", user.Role),
                    new Claim("userid", user.UserId.ToString())
                };

            claims.AddRange(permissions.Select(p => new Claim("permission", p)));

            var token = new JwtSecurityToken(
                issuer: _config["JwtSettings:Issuer"],
                audience: _config["JwtSettings:Audience"],
                claims: claims,
                expires: DateTime.UtcNow.AddMinutes(Convert.ToDouble(_config["JwtSettings:ExpirationMinutes"])),
                signingCredentials: creds);

            return new JwtSecurityTokenHandler().WriteToken(token);
        }
    }
}
