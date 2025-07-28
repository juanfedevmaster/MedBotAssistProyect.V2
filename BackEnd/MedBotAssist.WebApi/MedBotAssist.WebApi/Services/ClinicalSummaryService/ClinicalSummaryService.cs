using MedBotAssist.Interfaces;
using MedBotAssist.Models.Models;
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace MedBotAssist.WebApi.Services.ClinicalSummaryService
{
    /// <summary>
    /// Service for managing clinical summaries in the system.
    /// </summary>
    public class ClinicalSummaryService : IClinicalSummaryService
    {
        private readonly IMedBotAssistDbContext _context;

        /// <summary>
        /// Initializes a new instance of the <see cref="ClinicalSummaryService"/> class.
        /// </summary>
        /// <param name="context">The database context.</param>
        public ClinicalSummaryService(IMedBotAssistDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Creates a new clinical summary.
        /// </summary>
        /// <param name="summary">The clinical summary entity to create.</param>
        /// <returns>The created <see cref="ClinicalSummary"/>.</returns>
        public async Task<ClinicalSummary> CreateAsync(ClinicalSummary summary)
        {
            _context.ClinicalSummaries.Add(summary);
            await _context.SaveChangesAsync();
            return summary;
        }

        /// <summary>
        /// Gets a clinical summary by its ID.
        /// </summary>
        /// <param name="summaryId">The summary ID.</param>
        /// <returns>The <see cref="ClinicalSummary"/> if found; otherwise, null.</returns>
        public async Task<ClinicalSummary?> GetByIdAsync(int summaryId)
        {
            return await _context.ClinicalSummaries
                .Include(cs => cs.Note)
                .FirstOrDefaultAsync(cs => cs.SummaryId == summaryId);
        }

        /// <summary>
        /// Gets all clinical summaries.
        /// </summary>
        /// <returns>A list of all <see cref="ClinicalSummary"/> entities.</returns>
        public async Task<IEnumerable<ClinicalSummary>> GetAllAsync()
        {
            return await _context.ClinicalSummaries
                .Include(cs => cs.Note)
                .ToListAsync();
        }

        /// <summary>
        /// Updates an existing clinical summary.
        /// </summary>
        /// <param name="summary">The clinical summary entity with updated data.</param>
        /// <returns>The updated <see cref="ClinicalSummary"/> if found; otherwise, null.</returns>
        public async Task<ClinicalSummary?> UpdateAsync(ClinicalSummary summary)
        {
            var existing = await _context.ClinicalSummaries.FindAsync(summary.SummaryId);
            if (existing == null)
                return null;

            existing.NoteId = summary.NoteId;
            existing.Diagnosis = summary.Diagnosis;
            existing.Treatment = summary.Treatment;
            existing.Recommendations = summary.Recommendations;
            existing.NextSteps = summary.NextSteps;
            existing.GeneratedDate = summary.GeneratedDate;

            await _context.SaveChangesAsync();
            return existing;
        }

        /// <summary>
        /// Deletes a clinical summary by its ID.
        /// </summary>
        /// <param name="summaryId">The summary ID.</param>
        /// <returns>True if deleted; otherwise, false.</returns>
        public async Task<bool> DeleteAsync(int summaryId)
        {
            var summary = await _context.ClinicalSummaries.FindAsync(summaryId);
            if (summary == null)
                return false;

            _context.ClinicalSummaries.Remove(summary);
            await _context.SaveChangesAsync();
            return true;
        }
        /// <summary>
        /// Gets all clinical summaries for a specific patient, including medical notes and appointment details.
        /// </summary>
        /// <param name="patientId">The patient ID.</param>
        /// <returns>A list of clinical summaries for the patient.</returns>
        public async Task<IEnumerable<ClinicalSummary>> GetByPatientIdAsync(int patientId)
        {
            return await _context.ClinicalSummaries
                .Include(cs => cs.Note)
                    .ThenInclude(note => note.Appointment)
                        .ThenInclude(appointment => appointment.Patient)
                .Where(cs => cs.Note.Appointment.PatientId == patientId)
                .ToListAsync();
        }
    }
}
