using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;

namespace MedBotAssist.Models.Utils
{
    public static class ClinicalSummaryMapper
    {
        public static ClinicalSummaryReadDto ToReadDto(ClinicalSummary entity)
        {
            return new ClinicalSummaryReadDto
            {
                SummaryId = entity.SummaryId,
                NoteId = entity.NoteId,
                Diagnosis = entity.Diagnosis,
                Treatment = entity.Treatment,
                Recommendations = entity.Recommendations,
                NextSteps = entity.NextSteps,
                GeneratedDate = entity.GeneratedDate
            };
        }

        public static ClinicalSummary ToEntity(ClinicalSummaryCreateDto dto)
        {
            return new ClinicalSummary
            {
                NoteId = dto.NoteId,
                Diagnosis = dto.Diagnosis,
                Treatment = dto.Treatment,
                Recommendations = dto.Recommendations,
                NextSteps = dto.NextSteps,
                GeneratedDate = dto.GeneratedDate
            };
        }

        public static ClinicalSummary ToEntity(ClinicalSummaryResponseDto dto)
        {
            return new ClinicalSummary
            {
                NoteId = dto.MedicalNote.NoteId,
                Diagnosis = dto.Diagnosis,
                Treatment = dto.Treatment,
                Recommendations = dto.Recommendations,
                NextSteps = dto.NextSteps,
                GeneratedDate = dto.GeneratedDate
            };
        }

        public static ClinicalSummary ToEntity(ClinicalSummaryUpdateDto dto)
        {
            return new ClinicalSummary
            {
                SummaryId = dto.SummaryId,
                NoteId = dto.NoteId,
                Diagnosis = dto.Diagnosis,
                Treatment = dto.Treatment,
                Recommendations = dto.Recommendations,
                NextSteps = dto.NextSteps,
                GeneratedDate = dto.GeneratedDate
            };
        }
    }
}
