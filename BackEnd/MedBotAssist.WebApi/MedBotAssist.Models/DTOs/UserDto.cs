﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedBotAssist.Models.DTOs
{
    public class UserDto
    {
        public int UserId { get; set; }

        public string? FullName { get; set; }

        public string? Email { get; set; }

        public string? Role { get; set; }

        public bool? IsActive { get; set; }

        public DateTime? RegistrationDate { get; set; }

        public string UserName { get; set; } = null!;

        public string? Password { get; set; }

    }
}
