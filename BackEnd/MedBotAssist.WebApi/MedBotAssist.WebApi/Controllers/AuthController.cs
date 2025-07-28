using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace MedBotAssist.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IAuthOrchestrationService _authOrchestrationService;

        public AuthController(IAuthOrchestrationService authOrchestrationService)
        {
            _authOrchestrationService = authOrchestrationService;
        }

        /// <summary>
        /// Authenticates a user and returns the authentication token and DoctorId if applicable.
        /// </summary>
        [HttpPost("login")]
        public async Task<IActionResult> Login(LoginRequest request)
        {
            var result = await _authOrchestrationService.LoginWithDoctorInfoAsync(request);
            if (result == null)
                return Unauthorized("Invalid Credentials.");

            return Ok(result);
        }

        /// <summary>
        /// Registers a new user with the provided details.
        /// </summary>
        [HttpPost("register")]
        public async Task<IActionResult> Register(RegisterRequest request)
        {
            var result = await _authOrchestrationService.RegisterAsync(request);
            return Ok(result);
        }
    }
}
