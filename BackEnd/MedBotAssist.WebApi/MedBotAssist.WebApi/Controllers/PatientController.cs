using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Utils;
using MedBotAssist.WebApi.Services.AuthService;
using MedBotAssist.WebApi.Services.ClinicalSummaryService;
using Microsoft.AspNetCore.Mvc;

namespace MedBotAssist.WebApi.Controllers
{
    /// <summary>
    /// Controller for managing patient-related operations.
    /// Provides endpoints to create, retrieve, update, and delete patients.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class PatientController : ControllerBase
    {
        private readonly IPatientService _patientService;
        private readonly IClinicalSummaryService _clinicalSummaryService;

        /// <summary>
        /// Initializes a new instance of the <see cref="PatientController"/> class.
        /// </summary>
        /// <param name="patientService">Service for patient operations.</param>
        public PatientController(IPatientService patientService, IClinicalSummaryService clinicalSummaryService)
        {
            _patientService = patientService;
            _clinicalSummaryService = clinicalSummaryService;
        }

        /// <summary>
        /// Gets detailed information for a specific patient including clinical summaries and medical notes.
        /// </summary>
        /// <param name="patientId">The unique identifier of the patient.</param>
        /// <returns>The patient information with clinical summaries if found; otherwise, NotFound.</returns>
        /// <response code="200">Returns the patient information with clinical summaries.</response>
        /// <response code="404">If the patient is not found.</response>
        [HttpGet("getInfo")]
        [HasPermission("ViewPatients")]
        public async Task<ActionResult<PatientDetailedInfoResponseDto>> GetPatientInfo(int patientId)
        {
            var patient = await _patientService.GetByIdAsync(patientId);
            if (patient == null)
                return NotFound();

            var clinicalSummaries = await _clinicalSummaryService.GetByPatientIdAsync(patientId);

            var dto = PatientMapper.ToDetailedInfoResponseDto(patient, clinicalSummaries);
            return Ok(dto);
        }

        /// <summary>
        /// Creates a new patient.
        /// </summary>
        /// <param name="patientDto">The patient data to create.</param>
        /// <returns>The created patient information.</returns>
        /// <response code="201">Returns the created patient.</response>
        [HttpPost("create")]
        [HasPermission("ManagePatients")]
        public async Task<ActionResult<PatientInfoResponseDto>> CreatePatient([FromBody] PatientInfoResponseDto patientDto)
        {
            var patient = PatientMapper.ToPatient(patientDto);
            var created = await _patientService.CreateAsync(patient);
            var resultDto = PatientMapper.ToInfoResponseDto(created);
            return CreatedAtAction(nameof(GetPatientById), new { patientId = created.PatientId }, resultDto);
        }

        /// <summary>
        /// Gets a list of all patients.
        /// </summary>
        /// <returns>A list of patient information.</returns>
        /// <response code="200">Returns the list of patients.</response>
        [HttpGet("getAll")]
        [HasPermission("ViewPatients")]
        public async Task<ActionResult<IEnumerable<PatientInfoResponseDto>>> GetAllPatients()
        {
            var patients = await _patientService.GetAllAsync();
            var dtos = patients.Select(PatientMapper.ToInfoResponseDto).ToList();
            return Ok(dtos);
        }

        /// <summary>
        /// Gets a patient by their unique identifier.
        /// </summary>
        /// <param name="patientId">The unique identifier of the patient.</param>
        /// <returns>The patient information if found; otherwise, NotFound.</returns>
        /// <response code="200">Returns the patient information.</response>
        /// <response code="404">If the patient is not found.</response>
        [HttpGet("get/{patientId}")]
        [HasPermission("ViewPatients")]
        public async Task<ActionResult<PatientInfoResponseDto>> GetPatientById(int patientId)
        {
            var patient = await _patientService.GetByIdAsync(patientId);
            if (patient == null)
                return NotFound();

            var dto = PatientMapper.ToInfoResponseDto(patient);
            return Ok(dto);
        }

        /// <summary>
        /// Updates an existing patient.
        /// </summary>
        /// <param name="patientId">The patient's unique identifier.</param>
        /// <param name="patientDto">The updated patient data.</param>
        /// <returns>The updated patient if successful; otherwise, NotFound or BadRequest.</returns>
        /// <response code="200">Returns the updated patient.</response>
        /// <response code="400">If the patientId does not match the DTO.</response>
        /// <response code="404">If the patient is not found.</response>
        [HttpPut("update/{patientId}")]
        [HasPermission("ManagePatients")]
        public async Task<ActionResult<PatientInfoResponseDto>> UpdatePatient(int patientId, [FromBody] PatientInfoResponseDto patientDto)
        {
            if (patientId.ToString() != patientDto.PatientId)
                return BadRequest();

            var patientEntity = PatientMapper.ToPatient(patientDto);
            var updated = await _patientService.UpdateAsync(patientEntity);
            if (updated == null)
                return NotFound();

            var resultDto = PatientMapper.ToInfoResponseDto(updated);
            return Ok(resultDto);
        }

        /// <summary>
        /// Updates an existing patient.
        /// </summary>
        /// <param name="patientId">The patient's unique identifier.</param>
        /// <param name="patientDto">The updated patient data.</param>
        /// <returns>The updated patient if successful; otherwise, NotFound or BadRequest.</returns>
        /// <response code="200">Returns the updated patient.</response>
        /// <response code="400">If the patientId does not match the DTO.</response>
        /// <response code="404">If the patient is not found.</response>
        [HttpPut("update-patient")]
        [HasPermission("ManagePatients")]
        public async Task<ActionResult<PatientInfoResponseDto>> UpdatePatient([FromBody] PatientInfoResponseDto patientDto)
        {
            var patientEntity = PatientMapper.ToPatient(patientDto);
            var updated = await _patientService.UpdateAsync(patientEntity);
            if (updated == null)
                return NotFound();

            var resultDto = PatientMapper.ToInfoResponseDto(updated);
            return Ok(resultDto);
        }

        /// <summary>
        /// Deletes a patient by their unique identifier.
        /// </summary>
        /// <param name="patientId">The unique identifier of the patient to delete.</param>
        /// <returns>No content if deleted; otherwise, NotFound.</returns>
        /// <response code="204">If the patient was deleted.</response>
        /// <response code="404">If the patient is not found.</response>
        [HttpDelete("delete/{patientId}")]
        [HasPermission("ManagePatients")]
        public async Task<IActionResult> DeletePatient(int patientId)
        {
            var deleted = await _patientService.DeleteAsync(patientId);
            if (!deleted)
                return NotFound();

            return NoContent();
        }
    }
}
