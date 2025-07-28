using MedBotAssist.Models.Models;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace MedBotAssist.Interfaces
{
    public interface IAppointmentService
    {
        Task<Appointment> CreateAsync(Appointment appointment);
        Task<Appointment?> GetByIdAsync(int appointmentId);
        Task<IEnumerable<Appointment>> GetAllAsync();
        Task<Appointment?> UpdateAsync(Appointment appointment);
        Task<bool> DeleteAsync(int appointmentId);

        Task<IEnumerable<Appointment>> GetByDoctorIdAsync(int doctorId);
        Task<IEnumerable<Appointment>> GetByDoctorIdAndDateAsync(int doctorId, DateOnly date);
    }
}
