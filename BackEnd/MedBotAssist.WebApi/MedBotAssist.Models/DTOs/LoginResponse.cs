using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedBotAssist.Models.DTOs
{
    public class LoginResponse
    {
        public string UserName { get; set; }
        public string Token { get; set; }
        public int? DoctorId { get; set; }
    }
}
