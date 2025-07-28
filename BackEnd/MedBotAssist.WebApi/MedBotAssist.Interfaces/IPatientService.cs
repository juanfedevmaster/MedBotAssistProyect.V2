using MedBotAssist.Models.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace MedBotAssist.Interfaces
{
    public interface IPatientService
    {
        Task<Patient> CreateAsync(Patient patient);
        Task<Patient?> GetByIdAsync(int patientId);
        Task<IEnumerable<Patient>> GetAllAsync();
        Task<Patient?> UpdateAsync(Patient patient);
        Task<bool> DeleteAsync(int patientId);
    }
}
