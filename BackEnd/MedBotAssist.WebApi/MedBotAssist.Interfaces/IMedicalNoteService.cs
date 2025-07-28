using MedBotAssist.Models.DTOs;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedBotAssist.Interfaces
{
    public interface IMedicalNoteService
    {
        Task<bool> CreateMedicalNote(ClinicalSummaryResponseDto clinicalSummaryResponseDto);
    }
}
