using MedBotAssist.Interfaces;
using MedBotAssist.Models.Models;
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace MedBotAssist.WebApi.Services.AppointmentService
{
    /// <summary>
    /// Service for managing appointments in the system.
    /// </summary>
    public class AppointmentService : IAppointmentService
    {
        private readonly IMedBotAssistDbContext _context;

        /// <summary>
        /// Initializes a new instance of the <see cref="AppointmentService"/> class.
        /// </summary>
        /// <param name="context">The database context.</param>
        public AppointmentService(IMedBotAssistDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Creates a new appointment.
        /// </summary>
        /// <param name="appointment">The appointment entity to create.</param>
        /// <returns>The created <see cref="Appointment"/>.</returns>
        public async Task<Appointment> CreateAsync(Appointment appointment)
        {
            _context.Appointments.Add(appointment);
            await _context.SaveChangesAsync();
            return appointment;
        }

        /// <summary>
        /// Gets an appointment by its ID.
        /// </summary>
        /// <param name="appointmentId">The appointment ID.</param>
        /// <returns>The <see cref="Appointment"/> if found; otherwise, null.</returns>
        public async Task<Appointment?> GetByIdAsync(int appointmentId)
        {
            return await _context.Appointments
                .Include(a => a.Patient)
                .Include(a => a.Doctor)
                .FirstOrDefaultAsync(a => a.AppointmentId == appointmentId);
        }

        /// <summary>
        /// Gets all appointments.
        /// </summary>
        /// <returns>A list of all <see cref="Appointment"/> entities.</returns>
        public async Task<IEnumerable<Appointment>> GetAllAsync()
        {
            return await _context.Appointments
                .Include(a => a.Patient)
                .Include(a => a.Doctor)
                .ToListAsync();
        }

        /// <summary>
        /// Updates an existing appointment.
        /// </summary>
        /// <param name="appointment">The appointment entity with updated data.</param>
        /// <returns>The updated <see cref="Appointment"/> if found; otherwise, null.</returns>
        public async Task<Appointment?> UpdateAsync(Appointment appointment)
        {
            var existing = await _context.Appointments.FindAsync(appointment.AppointmentId);
            if (existing == null)
                return null;

            existing.PatientId = appointment.PatientId;
            existing.DoctorId = appointment.DoctorId;
            existing.AppointmentDate = appointment.AppointmentDate;
            existing.AppointmentTime = appointment.AppointmentTime;
            existing.Status = appointment.Status;
            existing.Notes = appointment.Notes;

            await _context.SaveChangesAsync();
            return existing;
        }

        /// <summary>
        /// Deletes an appointment by its ID.
        /// </summary>
        /// <param name="appointmentId">The appointment ID.</param>
        /// <returns>True if deleted; otherwise, false.</returns>
        public async Task<bool> DeleteAsync(int appointmentId)
        {
            var appointment = await _context.Appointments.FindAsync(appointmentId);
            if (appointment == null)
                return false;

            _context.Appointments.Remove(appointment);
            await _context.SaveChangesAsync();
            return true;
        }

        /// <summary>
        /// Gets all appointments for a specific doctor.
        /// </summary>
        /// <param name="doctorId">The doctor's ID.</param>
        /// <returns>A list of <see cref="Appointment"/> entities for the doctor.</returns>
        public async Task<IEnumerable<Appointment>> GetByDoctorIdAsync(int doctorId)
        {
            return await _context.Appointments
                .Include(a => a.Patient)
                .Include(a => a.Doctor)
                .Where(a => a.DoctorId == doctorId)
                .ToListAsync();
        }

        /// <summary>
        /// Gets all appointments for a specific doctor on a specific date.
        /// </summary>
        /// <param name="doctorId">The doctor's ID.</param>
        /// <param name="date">The date to filter appointments.</param>
        /// <returns>A list of <see cref="Appointment"/> entities for the doctor on the specified date.</returns>
        public async Task<IEnumerable<Appointment>> GetByDoctorIdAndDateAsync(int doctorId, DateOnly date)
        {
            return await _context.Appointments
                .Include(a => a.Patient)
                .Include(a => a.Doctor)
                .Where(a => a.DoctorId == doctorId && a.AppointmentDate == date)
                .ToListAsync();
        }
    }
}
