using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models
{
    public partial class Patient
    {
        public int PatientId { get; set; }

        public string? FullName { get; set; }

        public string? IdentificationNumber { get; set; }

        public DateOnly? BirthDate { get; set; }

        public string? Phone { get; set; }

        public string? Email { get; set; }

        public virtual ICollection<Appointment> Appointments { get; set; } = new List<Appointment>();
    }
}
