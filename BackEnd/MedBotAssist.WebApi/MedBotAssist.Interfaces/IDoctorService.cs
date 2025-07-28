using MedBotAssist.Models.Models;
using System.Threading.Tasks;

namespace MedBotAssist.Interfaces
{
    public interface IDoctorService
    {
        Task<Doctor?> GetDoctorInfoAsync(int doctorId);
        Task<Doctor?> UpdateDoctorProfileAsync(int doctorId, Doctor doctor, string userName);
    }
}
