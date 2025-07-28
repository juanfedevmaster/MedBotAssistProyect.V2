using MedBotAssist.Interfaces;
using MedBotAssist.Models.Models;
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace MedBotAssist.WebApi.Services.PatientService
{
    /// <summary>
    /// Service for managing patients in the system.
    /// </summary>
    public class PatientService : IPatientService
    {
        private readonly IMedBotAssistDbContext _context;

        /// <summary>
        /// Initializes a new instance of the <see cref="PatientService"/> class.
        /// </summary>
        /// <param name="context">The database context.</param>
        public PatientService(IMedBotAssistDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Creates a new patient.
        /// </summary>
        /// <param name="patient">The patient entity to create.</param>
        /// <returns>The created <see cref="Patient"/>.</returns>
        public async Task<Patient> CreateAsync(Patient patient)
        {
            _context.Patients.Add(patient);
            await _context.SaveChangesAsync();
            return patient;
        }

        /// <summary>
        /// Gets a patient by their ID.
        /// </summary>
        /// <param name="patientId">The patient's unique identifier.</param>
        /// <returns>The <see cref="Patient"/> if found; otherwise, null.</returns>
        public async Task<Patient?> GetByIdAsync(int patientId)
        {
            return await _context.Patients
                .Include(p => p.Appointments)
                .FirstOrDefaultAsync(p => p.PatientId == patientId);
        }

        /// <summary>
        /// Gets all patients.
        /// </summary>
        /// <returns>A list of all <see cref="Patient"/> entities.</returns>
        public async Task<IEnumerable<Patient>> GetAllAsync()
        {
            return await _context.Patients
                .Include(p => p.Appointments)
                .ToListAsync();
        }

        /// <summary>
        /// Updates an existing patient.
        /// </summary>
        /// <param name="patient">The patient entity with updated data.</param>
        /// <returns>The updated <see cref="Patient"/> if found; otherwise, null.</returns>
        public async Task<Patient?> UpdateAsync(Patient patient)
        {
            Patient existing = null;
            
            if(patient.PatientId != 0)
                existing = await _context.Patients.FindAsync(patient.PatientId);
            else
                existing = await _context.Patients
                    .FirstOrDefaultAsync(p => p.IdentificationNumber == patient.IdentificationNumber);

            if (existing == null)
                return null;

            existing.FullName = patient.FullName;
            existing.IdentificationNumber = patient.IdentificationNumber;
            existing.BirthDate = patient.BirthDate;
            existing.Phone = patient.Phone;
            existing.Email = patient.Email;

            await _context.SaveChangesAsync();
            return existing;
        }

        /// <summary>
        /// Deletes a patient by their ID.
        /// </summary>
        /// <param name="patientId">The patient's unique identifier.</param>
        /// <returns>True if deleted; otherwise, false.</returns>
        public async Task<bool> DeleteAsync(int patientId)
        {
            var patient = await _context.Patients.FindAsync(patientId);
            if (patient == null)
                return false;

            _context.Patients.Remove(patient);
            await _context.SaveChangesAsync();
            return true;
        }
    }
}
