using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Utils;
using MedBotAssist.WebApi.Services.AuthService;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using System.Threading.Tasks;

namespace MedBotAssist.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class DoctorController : ControllerBase
    {
        private readonly IDoctorService _doctorService;

        /// <summary>
        /// Initializes a new instance of the <see cref="DoctorController"/> class.
        /// Handles doctor profile and information endpoints.
        /// </summary>
        /// <param name="doctorService">Service for doctor operations.</param>
        public DoctorController(IDoctorService doctorService)
        {
            _doctorService = doctorService;
        }

        /// <summary>
        /// Gets the information of a doctor by their ID.
        /// </summary>
        /// <param name="doctorId">The doctor's unique identifier.</param>
        /// <returns>
        /// The <see cref="DoctorDto"/> with the doctor's information if found; otherwise, NotFound.
        /// </returns>
        /// <response code="200">Returns the doctor's information.</response>
        /// <response code="404">If the doctor is not found.</response>
        [HttpGet("getInfo/{doctorId}")]
        [HasPermission("ViewDoctors")]
        public async Task<ActionResult<DoctorDto>> GetDoctorInfo(int doctorId)
        {
            var doctor = await _doctorService.GetDoctorInfoAsync(doctorId);
            if (doctor == null)
                return NotFound();

            var dto = DoctorMapper.ToDto(doctor);
            return Ok(dto);
        }

        /// <summary>
        /// Updates the profile of a doctor. Only the doctor who owns the profile can update it.
        /// </summary>
        /// <param name="doctorId">The doctor's unique identifier.</param>
        /// <param name="doctorDto">The updated doctor profile data.</param>
        /// <returns>
        /// The updated <see cref="DoctorDto"/> if successful; otherwise, Forbid or Unauthorized.
        /// </returns>
        /// <response code="200">Returns the updated doctor profile.</response>
        /// <response code="401">If the user is not authenticated.</response>
        /// <response code="403">If the user is not allowed to update this profile.</response>
        [HttpPut("updateProfile/{doctorId}")]
        [HasPermission("ViewDoctors")]
        public async Task<ActionResult<DoctorDto>> UpdateDoctorProfile(int doctorId, [FromBody] DoctorDto doctorDto)
        {
            // Get the username from the JWT token
            var userName = User.FindFirstValue(ClaimTypes.Name);
            if (userName == null)
                return Unauthorized();

            var doctorEntity = DoctorMapper.ToEntity(doctorDto);
            var updated = await _doctorService.UpdateDoctorProfileAsync(doctorId, doctorEntity, userName);
            if (updated == null)
                return Forbid();

            var result = DoctorMapper.ToDto(updated);
            return Ok(result);
        }
    }
}
