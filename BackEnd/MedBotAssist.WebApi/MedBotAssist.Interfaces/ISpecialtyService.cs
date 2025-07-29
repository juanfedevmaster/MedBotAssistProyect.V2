using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedBotAssist.Interfaces
{
    public interface ISpecialtyService
    {
        Task<List<SpecialtyDto>> GetSpecialtyAll();
    }
}
