using MedBotAssist.Interfaces;
using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;
using MedBotAssist.Models.Utils;
using Microsoft.EntityFrameworkCore;

namespace MedBotAssist.WebApi.Services.SpecialtyService
{
    public class SpecialtyService : ISpecialtyService
    {
        private readonly IMedBotAssistDbContext _context;

        public SpecialtyService(IMedBotAssistDbContext context)
        {
            _context = context;
        }

        public async Task<List<SpecialtyDto>> GetSpecialtyAll()
        {
            var specialties = await _context.Specialties.ToListAsync();
            return SpecialtyMapper.ToDto(specialties);
        }
    }
}
