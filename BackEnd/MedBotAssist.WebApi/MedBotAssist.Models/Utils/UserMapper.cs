using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedBotAssist.Models.Utils
{
    public class UserMapper
    {
        public static UserDto ToDto(User user) { 
            return new UserDto
            {
                UserId = user.UserId,
                UserName = user.UserName,
                Email = user.Email,
                FullName = user.FullName,
                IsActive = user.IsActive
            };
        }
    }
}
