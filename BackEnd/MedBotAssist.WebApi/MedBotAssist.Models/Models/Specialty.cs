using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models
{
    public partial class Specialty
    {
        public int SpecialtyId { get; set; }

        public string? SpecialtyName { get; set; }

        public virtual ICollection<Doctor> Doctors { get; set; } = new List<Doctor>();
    }
}
