using MedBotAssist.Models.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace MedBotAssist.Interfaces
{
    public interface IClinicalSummaryService
    {
        Task<ClinicalSummary> CreateAsync(ClinicalSummary summary);
        Task<ClinicalSummary?> GetByIdAsync(int summaryId);
        Task<IEnumerable<ClinicalSummary>> GetAllAsync();
        Task<ClinicalSummary?> UpdateAsync(ClinicalSummary summary);
        Task<bool> DeleteAsync(int summaryId);
        Task<IEnumerable<ClinicalSummary>> GetByPatientIdAsync(int patientId); // Nuevo método
    }
}
