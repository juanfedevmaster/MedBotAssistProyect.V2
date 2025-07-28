using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models
{
    public partial class ClinicalSummary
    {
        public int SummaryId { get; set; }

        public int? NoteId { get; set; }

        public string? Diagnosis { get; set; }

        public string? Treatment { get; set; }

        public string? Recommendations { get; set; }

        public string? NextSteps { get; set; }

        public DateTime? GeneratedDate { get; set; }

        public virtual MedicalNote? Note { get; set; }
    }
}
