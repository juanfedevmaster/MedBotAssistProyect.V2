using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;
using MedBotAssist.Models.Utils;
using MedBotAssist.WebApi.Services.AuthService;
using Microsoft.AspNetCore.Mvc;

namespace MedBotAssist.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ClinicalSummaryController : ControllerBase
    {
        private readonly IClinicalSummaryService _service;

        /// <summary>
        /// Initializes a new instance of the <see cref="ClinicalSummaryController"/> class.
        /// </summary>
        /// <param name="service">Service for clinical summary operations.</param>
        public ClinicalSummaryController(IClinicalSummaryService service)
        {
            _service = service;
        }

        /// <summary>
        /// Creates a new clinical summary.
        /// </summary>
        /// <param name="dto">The clinical summary creation data.</param>
        /// <returns>The created clinical summary.</returns>
        /// <response code="201">Returns the created clinical summary.</response>
        [HttpPost("create")]
        [HasPermission("GenerateSummaries")]
        public async Task<ActionResult<ClinicalSummaryReadDto>> Create([FromBody] ClinicalSummaryCreateDto dto)
        {
            var entity = ClinicalSummaryMapper.ToEntity(dto);
            var created = await _service.CreateAsync(entity);
            var result = ClinicalSummaryMapper.ToReadDto(created);

            return CreatedAtAction(nameof(GetById), new { id = result.SummaryId }, result);
        }

        /// <summary>
        /// Updates an existing clinical summary.
        /// </summary>
        /// <param name="id">The summary ID.</param>
        /// <param name="dto">The updated clinical summary data.</param>
        /// <returns>The updated clinical summary if successful; otherwise, NotFound or BadRequest.</returns>
        /// <response code="200">Returns the updated clinical summary.</response>
        /// <response code="400">If the ID does not match the DTO.</response>
        /// <response code="404">If the summary is not found.</response>
        [HttpPut("update/{id}")]
        [HasPermission("GenerateSummaries")]
        public async Task<ActionResult<ClinicalSummaryReadDto>> Update(int id, [FromBody] ClinicalSummaryUpdateDto dto)
        {
            if (id != dto.SummaryId)
                return BadRequest();

            var entity = ClinicalSummaryMapper.ToEntity(dto);
            var updated = await _service.UpdateAsync(entity);
            if (updated == null)
                return NotFound();

            var result = ClinicalSummaryMapper.ToReadDto(updated);
            return Ok(result);
        }

        /// <summary>
        /// Gets a clinical summary by its ID.
        /// </summary>
        /// <param name="id">The summary ID.</param>
        /// <returns>The clinical summary if found; otherwise, NotFound.</returns>
        /// <response code="200">Returns the clinical summary.</response>
        /// <response code="404">If the summary is not found.</response>
        [HttpGet("get/{id}")]
        [HasPermission("GenerateSummaries")]
        public async Task<ActionResult<ClinicalSummaryReadDto>> GetById(int id)
        {
            var summary = await _service.GetByIdAsync(id);
            if (summary == null)
                return NotFound();

            var result = ClinicalSummaryMapper.ToReadDto(summary);
            return Ok(result);
        }

        /// <summary>
        /// Gets all clinical summaries.
        /// </summary>
        /// <returns>A list of all clinical summaries.</returns>
        /// <response code="200">Returns the list of clinical summaries.</response>
        [HttpGet("getall")]
        [HasPermission("GenerateSummaries")]
        public async Task<ActionResult<IEnumerable<ClinicalSummaryReadDto>>> GetAll()
        {
            var summaries = await _service.GetAllAsync();
            var result = summaries.Select(ClinicalSummaryMapper.ToReadDto);
            return Ok(result);
        }

        /// <summary>
        /// Deletes a clinical summary by its ID.
        /// </summary>
        /// <param name="id">The summary ID.</param>
        /// <returns>NoContent if deleted; otherwise, NotFound.</returns>
        /// <response code="204">If the summary was deleted.</response>
        /// <response code="404">If the summary is not found.</response>
        [HttpDelete("delete/{id}")]
        [HasPermission("GenerateSummaries")]
        public async Task<IActionResult> Delete(int id)
        {
            var deleted = await _service.DeleteAsync(id);
            if (!deleted)
                return NotFound();

            return NoContent();
        }
    }
}