using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.WebApi.Services.AuthService;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace MedBotAssist.WebApi.Controllers
{
    /// <summary>
    /// API controller for managing medical notes.
    /// </summary>
    /// <remarks>
    /// Provides endpoints to create new medical notes.
    /// </remarks>
    [Route("api/[controller]")]
    [ApiController]
    public class MedicalNoteController : ControllerBase
    {
        private readonly IMedicalNoteService medicalNoteService;

        /// <summary>
        /// Initializes a new instance of the <see cref="MedicalNoteController"/> class.
        /// </summary>
        /// <param name="medicalNoteService">Service for handling medical note operations.</param>
        public MedicalNoteController(IMedicalNoteService medicalNoteService)
        {
            this.medicalNoteService = medicalNoteService;
        }

        /// <summary>
        /// Creates a new medical note.
        /// </summary>
        /// <param name="medicalNoteResponseDto">The medical note data to create.</param>
        /// <returns>
        /// Returns 200 OK if the note is created successfully, 
        /// 400 Bad Request if the input is invalid, 
        /// or 500 Internal Server Error if creation fails.
        /// </returns>
        [HttpPost("CreateMedicalNote")]
        [HasPermission("EditMedicalNotes")]
        public async Task<IActionResult> CreateMedicalNote([FromBody] ClinicalSummaryResponseDto clinicalSummaryResponseDto)
        {
            if (clinicalSummaryResponseDto == null)
            {
                return BadRequest("Medical note data is required.");
            }

            var result = await medicalNoteService.CreateMedicalNote(clinicalSummaryResponseDto);
            if (result)
            {
                return Ok("Medical note created successfully.");
            }
            else
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Failed to create medical note.");
            }
        }
    }
}
