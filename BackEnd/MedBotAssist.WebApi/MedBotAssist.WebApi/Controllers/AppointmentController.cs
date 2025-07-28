using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;
using MedBotAssist.Models.Utils;
using MedBotAssist.WebApi.Services.AuthService;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace MedBotAssist.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AppointmentController : ControllerBase
    {
        private readonly IAppointmentService _appointmentService;

        public AppointmentController(IAppointmentService appointmentService)
        {
            _appointmentService = appointmentService;
        }

        /// <summary>
        /// Creates a new appointment.
        /// </summary>
        /// <param name="appointmentDto">The appointment data.</param>
        /// <returns>The created appointment.</returns>
        [HttpPost("create")]
        [HasPermission("ManageAppointments")]
        public async Task<ActionResult<AppointmentDto>> Create([FromBody] AppointmentDto appointmentDto)
        {
            var entity = AppointmentMapper.ToEntity(appointmentDto);
            var created = await _appointmentService.CreateAsync(entity);
            var result = AppointmentMapper.ToDto(created);
            return CreatedAtAction(nameof(GetById), new { appointmentId = result.AppointmentId }, result);
        }

        /// <summary>
        /// Gets an appointment by its ID.
        /// </summary>
        /// <param name="appointmentId">The appointment ID.</param>
        /// <returns>The appointment if found; otherwise, NotFound.</returns>
        [HttpGet("get/{appointmentId}")]
        [HasPermission("ViewAppointments")]
        public async Task<ActionResult<AppointmentDto>> GetById(int appointmentId)
        {
            var appointment = await _appointmentService.GetByIdAsync(appointmentId);
            if (appointment == null)
                return NotFound();

            var dto = AppointmentMapper.ToDto(appointment);
            return Ok(dto);
        }

        /// <summary>
        /// Gets all appointments.
        /// </summary>
        /// <returns>A list of all appointments.</returns>
        [HttpGet("getAll")]
        [HasPermission("ViewAppointments")]
        public async Task<ActionResult<IEnumerable<AppointmentDto>>> GetAll()
        {
            var appointments = await _appointmentService.GetAllAsync();
            var dtos = appointments.Select(AppointmentMapper.ToDto).ToList();
            return Ok(dtos);
        }

        /// <summary>
        /// Updates an existing appointment.
        /// </summary>
        /// <param name="appointmentId">The appointment ID.</param>
        /// <param name="appointmentDto">The updated appointment data.</param>
        /// <returns>The updated appointment if successful; otherwise, NotFound or BadRequest.</returns>
        [HttpPut("update/{appointmentId}")]
        [HasPermission("ManageAppointments")]
        public async Task<ActionResult<AppointmentDto>> Update(int appointmentId, [FromBody] AppointmentDto appointmentDto)
        {
            if (appointmentId != appointmentDto.AppointmentId)
                return BadRequest();

            var entity = AppointmentMapper.ToEntity(appointmentDto);
            var updated = await _appointmentService.UpdateAsync(entity);
            if (updated == null)
                return NotFound();

            var result = AppointmentMapper.ToDto(updated);
            return Ok(result);
        }

        /// <summary>
        /// Deletes an appointment by its ID.
        /// </summary>
        /// <param name="appointmentId">The appointment ID.</param>
        /// <returns>NoContent if deleted; otherwise, NotFound.</returns>
        [HttpDelete("delete/{appointmentId}")]
        [HasPermission("ManageAppointments")]
        public async Task<IActionResult> Delete(int appointmentId)
        {
            var deleted = await _appointmentService.DeleteAsync(appointmentId);
            if (!deleted)
                return NotFound();

            return NoContent();
        }

        /// <summary>
        /// Gets all appointments for a specific doctor.
        /// </summary>
        /// <param name="doctorId">The doctor's ID.</param>
        /// <returns>A list of appointments for the doctor.</returns>
        [HttpGet("getByDoctor/{doctorId}")]
        [HasPermission("ViewAppointments")]
        public async Task<ActionResult<IEnumerable<AppointmentDto>>> GetByDoctorId(int doctorId)
        {
            var appointments = await _appointmentService.GetByDoctorIdAsync(doctorId);
            var dtos = appointments.Select(AppointmentMapper.ToDto).ToList();
            return Ok(dtos);
        }

        /// <summary>
        /// Gets all appointments for a specific doctor on a specific date.
        /// </summary>
        /// <param name="doctorId">The doctor's ID.</param>
        /// <param name="date">The date in yyyy-MM-dd format.</param>
        /// <returns>A list of appointments for the doctor on the specified date.</returns>
        [HttpGet("getByDoctorAndDate/{doctorId}/{date}")]
        [HasPermission("ViewAppointments")]
        public async Task<ActionResult<IEnumerable<AppointmentDto>>> GetByDoctorIdAndDate(int doctorId, string date)
        {
            if (!DateOnly.TryParse(date, out var parsedDate))
                return BadRequest("Invalid date format. Use yyyy-MM-dd.");

            var appointments = await _appointmentService.GetByDoctorIdAndDateAsync(doctorId, parsedDate);
            var dtos = appointments.Select(AppointmentMapper.ToDto).ToList();
            return Ok(dtos);
        }
    }
}
