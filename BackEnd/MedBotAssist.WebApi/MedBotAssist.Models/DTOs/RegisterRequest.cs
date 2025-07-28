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


        public RegisterRequest() { }
    }
}
