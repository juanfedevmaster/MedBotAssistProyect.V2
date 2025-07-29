using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedBotAssist.Models.Utils
{
    public class SpecialtyMapper
    {
        public static List<SpecialtyDto> ToDto(List<Specialty> specialties)
        {
            return specialties.Select(x=> new SpecialtyDto
            {
                SpecialtyId = x.SpecialtyId,
                SpecialtyName = x.SpecialtyName
            }).ToList();
        }
    }
}
