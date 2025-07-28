using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;

namespace MedBotAssist.Models.Utils
{
    public static class AppointmentMapper
    {
        public static AppointmentDto ToDto(Appointment appointment)
        {
            return new AppointmentDto
            {
                AppointmentId = appointment.AppointmentId,
                PatientId = appointment.PatientId,
                DoctorId = appointment.DoctorId,
                AppointmentDate = appointment.AppointmentDate,
                AppointmentTime = appointment.AppointmentTime,
                Status = appointment.Status,
                Notes = appointment.Notes
            };
        }

        public static Appointment ToEntity(AppointmentDto dto)
        {
            return new Appointment
            {
                AppointmentId = dto.AppointmentId,
                PatientId = dto.PatientId,
                DoctorId = dto.DoctorId,
                AppointmentDate = dto.AppointmentDate,
                AppointmentTime = dto.AppointmentTime,
                Status = dto.Status,
                Notes = dto.Notes
            };
        }
    }
}
