namespace MedBotAssist.Models.DTOs
{
    public class DoctorDto
    {
        public int DoctorId { get; set; }
        public int? UserId { get; set; }
        public int? SpecialtyId { get; set; }
        public string? MedicalLicenseNumber { get; set; }
        public string? SpecialtyName { get; set; }
        public string? UserName { get; set; }
    }
}
