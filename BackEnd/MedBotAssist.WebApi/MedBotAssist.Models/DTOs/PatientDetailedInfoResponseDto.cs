using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.DTOs
{
    public class PatientDetailedInfoResponseDto : PatientInfoResponseDto
    {
        public IEnumerable<ClinicalSummaryResponseDto> ClinicalSummaries { get; set; } = new List<ClinicalSummaryResponseDto>();
    }
}