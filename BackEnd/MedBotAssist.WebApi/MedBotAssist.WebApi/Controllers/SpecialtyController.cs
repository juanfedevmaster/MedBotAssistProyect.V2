using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Utils;
using MedBotAssist.WebApi.Services.ClinicalSummaryService;
using MedBotAssist.WebApi.Services.PatientService;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace MedBotAssist.WebApi.Controllers
{
    /// <summary>
    /// API controller for managing medical specialties.
    /// </summary>
    /// <remarks>
    /// Provides endpoints to retrieve information about available medical specialties.
    /// </remarks>
    [Route("api/[controller]")]
    [ApiController]
    public class SpecialtyController : ControllerBase
    {
        private readonly ISpecialtyService _specialtyService;

        /// <summary>
        /// Initializes a new instance of the <see cref="SpecialtyController"/> class.
        /// </summary>
        /// <param name="specialtyService">Service for handling specialty-related operations.</param>
        public SpecialtyController(ISpecialtyService specialtyService)
        {
            _specialtyService = specialtyService;
        }

        /// <summary>
        /// Retrieves all available medical specialties.
        /// </summary>
        /// <returns>
        /// A list of <see cref="SpecialtyDto"/> objects representing the available specialties.
        /// Returns 200 OK with the list on success.
        /// </returns>
        [HttpGet("getAll")]
        public async Task<ActionResult<List<SpecialtyDto>>> GetAll()
        {
            return Ok(await _specialtyService.GetSpecialtyAll());
        }
    }
}
