using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models
{
    public partial class MedicalNote
    {
        public int NoteId { get; set; }

        public int? AppointmentId { get; set; }

        public DateTime? CreationDate { get; set; }

        public string? FreeText { get; set; }

        public virtual Appointment? Appointment { get; set; }

        public virtual ICollection<ClinicalSummary> ClinicalSummaries { get; set; } = new List<ClinicalSummary>();
    }
}
