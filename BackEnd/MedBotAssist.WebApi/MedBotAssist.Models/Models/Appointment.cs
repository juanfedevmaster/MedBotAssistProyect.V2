using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models
{
    public partial class Appointment
    {
        public int AppointmentId { get; set; }

        public int? PatientId { get; set; }

        public int? DoctorId { get; set; }

        public DateOnly? AppointmentDate { get; set; }

        public TimeOnly? AppointmentTime { get; set; }

        public string? Status { get; set; }

        public string? Notes { get; set; }

        public virtual Doctor? Doctor { get; set; }

        public virtual ICollection<MedicalNote> MedicalNotes { get; set; } = new List<MedicalNote>();

        public virtual Patient? Patient { get; set; }
    }
}
