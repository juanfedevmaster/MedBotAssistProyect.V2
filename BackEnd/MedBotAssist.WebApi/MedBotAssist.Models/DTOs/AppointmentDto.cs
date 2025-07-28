using System;

namespace MedBotAssist.Models.DTOs
{
    public class AppointmentDto
    {
        public int AppointmentId { get; set; }
        public int? PatientId { get; set; }
        public int? DoctorId { get; set; }
        public DateOnly? AppointmentDate { get; set; }
        public TimeOnly? AppointmentTime { get; set; }
        public string? Status { get; set; }
        public string? Notes { get; set; }
    }
}
