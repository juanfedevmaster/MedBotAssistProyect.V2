using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using Microsoft.EntityFrameworkCore;
using System.Threading.Tasks;

namespace MedBotAssist.WebApi.Services.OrchestrationService
{
    public class AuthOrchestrationService : IAuthOrchestrationService
    {
        private readonly IAuthService _authService;
        private readonly IMedBotAssistDbContext _context;

        public AuthOrchestrationService(IAuthService authService, IMedBotAssistDbContext context)
        {
            _authService = authService;
            _context = context;
        }

        public async Task<LoginResponse> LoginWithDoctorInfoAsync(LoginRequest request)
        {
            var result = await _authService.LoginAsync(request);
            if (result == null)
                return null;

            var user = await _context.Users.FirstOrDefaultAsync(u => u.UserName == request.UserName);
            if (user != null)
            {
                var doctor = await _context.Doctors.FirstOrDefaultAsync(d => d.UserId == user.UserId);
                if (doctor != null)
                {
                    // Asegúrate de que LoginResponse tenga DoctorId
                    result.DoctorId = doctor.DoctorId;
                }
            }
            return result;
        }

        public async Task<string> RegisterAsync(RegisterRequest request)
        {
            return await _authService.RegisterAsync(request);
        }
    }
}
