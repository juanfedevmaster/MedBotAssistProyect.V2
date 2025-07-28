using System;
using System.Collections.Generic;

namespace MedBotAssist.Models.Models
{
    public partial class User
    {
        public int UserId { get; set; }

        public string? FullName { get; set; }

        public string? Email { get; set; }

        public string? Role { get; set; }

        public bool? IsActive { get; set; }

        public DateTime? RegistrationDate { get; set; }

        public string UserName { get; set; } = null!;

        public string? Password { get; set; }

        public virtual ICollection<Alert> Alerts { get; set; } = new List<Alert>();

        public virtual ICollection<ChatbotInteraction> ChatbotInteractions { get; set; } = new List<ChatbotInteraction>();

        public virtual ICollection<Doctor> Doctors { get; set; } = new List<Doctor>();

        public virtual ICollection<Token> Tokens { get; set; } = new List<Token>();

        public virtual ICollection<UserRole> UserRoles { get; set; } = new List<UserRole>();
    }
}
