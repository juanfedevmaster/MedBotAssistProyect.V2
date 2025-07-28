using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedBotAssist.Models.DTOs
{
    public class ClinicalSummaryUpdateDto
    {
        public int SummaryId { get; set; }
        public int? NoteId { get; set; }
        public string? Diagnosis { get; set; }
        public string? Treatment { get; set; }
        public string? Recommendations { get; set; }
        public string? NextSteps { get; set; }
        public DateTime? GeneratedDate { get; set; }
    }
}
