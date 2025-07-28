using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedBotAssist.Models.DTOs
{
    public class MedicalNoteResponseDto
    {
        public int NoteId { get; set; }
        public DateTime? CreationDate { get; set; }
        public string FreeText { get; set; }
        public int? AppointmentId { get; set; }
    }
}
