using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models
{

    public partial class Doctor
    {
        public int DoctorId { get; set; }

        public int? UserId { get; set; }

        public int? SpecialtyId { get; set; }

        public string? MedicalLicenseNumber { get; set; }

        public virtual ICollection<Appointment> Appointments { get; set; } = new List<Appointment>();

        public virtual ICollection<DoctorSchedule> DoctorSchedules { get; set; } = new List<DoctorSchedule>();

        public virtual Specialty? Specialty { get; set; }

        public virtual User? User { get; set; }
    }
}
