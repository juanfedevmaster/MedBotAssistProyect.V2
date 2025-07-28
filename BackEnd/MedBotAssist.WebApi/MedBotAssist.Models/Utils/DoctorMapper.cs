using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;

namespace MedBotAssist.Models.Utils
{
    public static class DoctorMapper
    {
        public static DoctorDto ToDto(Doctor doctor)
        {
            return new DoctorDto
            {
                DoctorId = doctor.DoctorId,
                UserId = doctor.UserId,
                SpecialtyId = doctor.SpecialtyId,
                MedicalLicenseNumber = doctor.MedicalLicenseNumber,
                SpecialtyName = doctor.Specialty?.SpecialtyName,
                UserName = doctor.User?.UserName
            };
        }

        public static Doctor ToEntity(DoctorDto dto)
        {
            return new Doctor
            {
                DoctorId = dto.DoctorId,
                UserId = dto.UserId,
                SpecialtyId = dto.SpecialtyId,
                MedicalLicenseNumber = dto.MedicalLicenseNumber
            };
        }
    }
}
