using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.DTOs
{
    public class PatientDetailedInfoResponseDto : PatientInfoResponseDto
    {
        public IEnumerable<ClinicalSummaryResponseDto> ClinicalSummaries { get; set; } = new List<ClinicalSummaryResponseDto>();
    }

    public class ClinicalSummaryResponseDto
    {
        public int SummaryId { get; set; }
        public string? Diagnosis { get; set; }
        public string? Treatment { get; set; }
        public string? Recommendations { get; set; }
        public string? NextSteps { get; set; }
        public DateTime? GeneratedDate { get; set; }
        public MedicalNoteResponseDto? MedicalNote { get; set; }
    }

    public class MedicalNoteResponseDto
    {
        public int NoteId { get; set; }
        public DateTime? CreationDate { get; set; }
        public string? FreeText { get; set; }
        public int? AppointmentId { get; set; }
    }
}