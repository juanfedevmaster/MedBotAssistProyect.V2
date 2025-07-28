using MedBotAssist.Models.Models;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace MedBotAssist.Interfaces
{
    public interface IMedBotAssistDbContext
    {

        DbSet<Alert> Alerts { get; set; }
        DbSet<Appointment> Appointments { get; set; }
        DbSet<ChatbotInteraction> ChatbotInteractions { get; set; }
        DbSet<ClinicalSummary> ClinicalSummaries { get; set; }
        DbSet<Doctor> Doctors { get; set; }
        DbSet<DoctorSchedule> DoctorSchedules { get; set; }
        DbSet<MedicalNote> MedicalNotes { get; set; }
        DbSet<Patient> Patients { get; set; }
        DbSet<Permission> Permissions { get; set; }
        DbSet<Role> Roles { get; set; }
        DbSet<RolePermission> RolePermissions { get; set; }
        DbSet<Specialty> Specialties { get; set; }
        DbSet<Token> Tokens { get; set; }
        DbSet<User> Users { get; set; }
        DbSet<UserRole> UserRoles { get; set; }
        Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
    }
}
