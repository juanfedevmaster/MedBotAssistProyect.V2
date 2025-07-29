using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;
using MedBotAssist.Models.Utils;

namespace MedBotAssist.WebApi.Services.MedicalNoteService
{
    public class MedicalNoteService : IMedicalNoteService
    {
        private readonly IMedBotAssistDbContext _context;

        /// <summary>
        /// Initializes a new instance of the <see cref="MedicalNoteService"/> class.
        /// </summary>
        /// <param name="context">The database context.</param>
        public MedicalNoteService(IMedBotAssistDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Creates a new medical note in the database based on the provided MedicalNoteResponseDto.
        /// </summary>
        /// <param name="medicalNoteResponseDto">The DTO containing the information for the medical note to be created.</param>
        /// <returns>
        /// A task that represents the asynchronous operation. The task result contains true if the medical note was created successfully; otherwise, false.
        /// </returns>
        public async Task<bool> CreateMedicalNote(ClinicalSummaryResponseDto clinicalSummaryResponseDto)
        {
            if (clinicalSummaryResponseDto == null)
                return false;

            var medicalNote = PatientMapper.MedicalNoteDTOToMedicalNote(clinicalSummaryResponseDto.MedicalNote);
            
            await _context.MedicalNotes.AddAsync(medicalNote);
            await _context.SaveChangesAsync();

            clinicalSummaryResponseDto.MedicalNote.NoteId = medicalNote.NoteId;

            var clinicalSummary = ClinicalSummaryMapper.ToEntity(clinicalSummaryResponseDto);

            await _context.ClinicalSummaries.AddAsync(clinicalSummary);
            var result = await _context.SaveChangesAsync();

            return result > 0;
        }
    }
}
