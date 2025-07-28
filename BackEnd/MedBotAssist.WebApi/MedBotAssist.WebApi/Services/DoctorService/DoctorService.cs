using MedBotAssist.Interfaces;
using MedBotAssist.Models.Models;
using Microsoft.EntityFrameworkCore;
using System.Threading.Tasks;

namespace MedBotAssist.WebApi.Services.DoctorService
{
    /// <summary>
    /// Service for managing doctor profiles and information.
    /// </summary>
    public class DoctorService : IDoctorService
    {
        private readonly IMedBotAssistDbContext _context;

        /// <summary>
        /// Initializes a new instance of the <see cref="DoctorService"/> class.
        /// </summary>
        /// <param name="context">The database context.</param>
        public DoctorService(IMedBotAssistDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Gets the information of a doctor by their ID.
        /// </summary>
        /// <param name="doctorId">The doctor's unique identifier.</param>
        /// <returns>
        /// The <see cref="Doctor"/> entity if found; otherwise, null.
        /// </returns>
        public async Task<Doctor?> GetDoctorInfoAsync(int doctorId)
        {
            return await _context.Doctors
                .Include(d => d.Specialty)
                .Include(d => d.User)
                .FirstOrDefaultAsync(d => d.DoctorId == doctorId);
        }

        /// <summary>
        /// Updates the profile of a doctor. Only the doctor who owns the profile can update it.
        /// </summary>
        /// <param name="doctorId">The doctor's unique identifier.</param>
        /// <param name="doctor">The updated doctor profile data.</param>
        /// <param name="userName">The username of the user attempting the update.</param>
        /// <returns>
        /// The updated <see cref="Doctor"/> entity if successful; otherwise, null.
        /// </returns>
        public async Task<Doctor?> UpdateDoctorProfileAsync(int doctorId, Doctor doctor, string userName)
        {
            var existing = await _context.Doctors
                .Include(d => d.User)
                .FirstOrDefaultAsync(d => d.DoctorId == doctorId);

            if (existing == null || existing.User == null || existing.User.UserName != userName)
                return null;

            existing.MedicalLicenseNumber = doctor.MedicalLicenseNumber;
            existing.SpecialtyId = doctor.SpecialtyId;

            await _context.SaveChangesAsync();
            return existing;
        }
    }
}
