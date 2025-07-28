using MedBotAssist.Models.DTOs;
using System.Threading.Tasks;

namespace MedBotAssist.Interfaces
{
    public interface IAuthOrchestrationService
    {
        Task<LoginResponse> LoginWithDoctorInfoAsync(LoginRequest request);
        Task<string> RegisterAsync(RegisterRequest request);
    }
}
