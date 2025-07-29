using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedBotAssist.Models.DTOs
{
    public class RegisterRequest
    {
        public string FullName { get; set; }
        public string Email { get; set; }
        public string UserName { get; set; }
        public string Password { get; set; }
        public int? RoleId { get; set; } = 2; // Default to User role
        public int? SpecialtyId { get; set; }
        public string? MedicalLicenseNumber { get; set; }

        public RegisterRequest() { }
    }
}
