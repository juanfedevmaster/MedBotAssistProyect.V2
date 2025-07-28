using System;
using System.Collections.Generic;
using MedBotAssist.Interfaces;
using MedBotAssist.Models.Models;
using Microsoft.EntityFrameworkCore;

namespace MedBotAssist.Persistance.Context;

public partial class MedBotAssistDbContext : DbContext, IMedBotAssistDbContext 
{
    public MedBotAssistDbContext()
    {
    }

    public MedBotAssistDbContext(DbContextOptions<MedBotAssistDbContext> options)
        : base(options)
    {
    }

    public virtual DbSet<Alert> Alerts { get; set; }

    public virtual DbSet<Appointment> Appointments { get; set; }

    public virtual DbSet<ChatbotInteraction> ChatbotInteractions { get; set; }

    public virtual DbSet<ClinicalSummary> ClinicalSummaries { get; set; }

    public virtual DbSet<Doctor> Doctors { get; set; }

    public virtual DbSet<DoctorSchedule> DoctorSchedules { get; set; }

    public virtual DbSet<MedicalNote> MedicalNotes { get; set; }

    public virtual DbSet<Patient> Patients { get; set; }

    public virtual DbSet<Permission> Permissions { get; set; }

    public virtual DbSet<Role> Roles { get; set; }

    public virtual DbSet<RolePermission> RolePermissions { get; set; }

    public virtual DbSet<Specialty> Specialties { get; set; }

    public virtual DbSet<Token> Tokens { get; set; }

    public virtual DbSet<User> Users { get; set; }

    public virtual DbSet<UserRole> UserRoles { get; set; }

    public Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
            => base.SaveChangesAsync(cancellationToken);


    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Alert>(entity =>
        {
            entity.HasKey(e => e.AlertId).HasName("PK__Alerts__EBB16A8D0F2DD021");

            entity.Property(e => e.AlertDate)
                .HasDefaultValueSql("(getdate())")
                .HasColumnType("datetime");
            entity.Property(e => e.AlertType).HasMaxLength(100);
            entity.Property(e => e.IsRead).HasDefaultValue(false);
            entity.Property(e => e.Message).HasMaxLength(255);

            entity.HasOne(d => d.User).WithMany(p => p.Alerts)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("FK__Alerts__UserId__7C4F7684");
        });

        modelBuilder.Entity<Appointment>(entity =>
        {
            entity.HasKey(e => e.AppointmentId).HasName("PK__Appointm__8ECDFCC2412F3134");

            entity.Property(e => e.Notes).HasMaxLength(255);
            entity.Property(e => e.Status)
                .HasMaxLength(20)
                .HasDefaultValue("Pending");

            entity.HasOne(d => d.Doctor).WithMany(p => p.Appointments)
                .HasForeignKey(d => d.DoctorId)
                .HasConstraintName("FK__Appointme__Docto__6D0D32F4");

            entity.HasOne(d => d.Patient).WithMany(p => p.Appointments)
                .HasForeignKey(d => d.PatientId)
                .HasConstraintName("FK__Appointme__Patie__6C190EBB");
        });

        modelBuilder.Entity<ChatbotInteraction>(entity =>
        {
            entity.HasKey(e => e.InteractionId).HasName("PK__ChatbotI__922C04964EF36970");

            entity.Property(e => e.InteractionType).HasMaxLength(50);
            entity.Property(e => e.Timestamp)
                .HasDefaultValueSql("(getdate())")
                .HasColumnType("datetime");

            entity.HasOne(d => d.User).WithMany(p => p.ChatbotInteractions)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("FK__ChatbotIn__UserI__787EE5A0");
        });

        modelBuilder.Entity<ClinicalSummary>(entity =>
        {
            entity.HasKey(e => e.SummaryId).HasName("PK__Clinical__DAB10E2FDD101B15");

            entity.Property(e => e.Diagnosis).HasMaxLength(255);
            entity.Property(e => e.GeneratedDate)
                .HasDefaultValueSql("(getdate())")
                .HasColumnType("datetime");
            entity.Property(e => e.NextSteps).HasMaxLength(255);
            entity.Property(e => e.Recommendations).HasMaxLength(255);
            entity.Property(e => e.Treatment).HasMaxLength(255);

            entity.HasOne(d => d.Note).WithMany(p => p.ClinicalSummaries)
                .HasForeignKey(d => d.NoteId)
                .HasConstraintName("FK__ClinicalS__NoteI__74AE54BC");
        });

        modelBuilder.Entity<Doctor>(entity =>
        {
            entity.HasKey(e => e.DoctorId).HasName("PK__Doctors__2DC00EBF3EA91500");

            entity.Property(e => e.MedicalLicenseNumber).HasMaxLength(50);

            entity.HasOne(d => d.Specialty).WithMany(p => p.Doctors)
                .HasForeignKey(d => d.SpecialtyId)
                .HasConstraintName("FK__Doctors__Special__6477ECF3");

            entity.HasOne(d => d.User).WithMany(p => p.Doctors)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("FK__Doctors__UserId__6383C8BA");
        });

        modelBuilder.Entity<DoctorSchedule>(entity =>
        {
            entity.HasKey(e => e.ScheduleId).HasName("PK__DoctorSc__9C8A5B496E2C32D8");

            entity.Property(e => e.DayOfWeek).HasMaxLength(10);

            entity.HasOne(d => d.Doctor).WithMany(p => p.DoctorSchedules)
                .HasForeignKey(d => d.DoctorId)
                .HasConstraintName("FK__DoctorSch__Docto__693CA210");
        });

        modelBuilder.Entity<MedicalNote>(entity =>
        {
            entity.HasKey(e => e.NoteId).HasName("PK__MedicalN__EACE355F4B13212B");

            entity.Property(e => e.CreationDate)
                .HasDefaultValueSql("(getdate())")
                .HasColumnType("datetime");
            entity.Property(e => e.FreeText).IsUnicode(false);

            entity.HasOne(d => d.Appointment).WithMany(p => p.MedicalNotes)
                .HasForeignKey(d => d.AppointmentId)
                .HasConstraintName("FK__MedicalNo__Appoi__70DDC3D8");
        });

        modelBuilder.Entity<Patient>(entity =>
        {
            entity.HasKey(e => e.PatientId).HasName("PK__Patients__970EC366F2F437A8");

            entity.Property(e => e.Email).HasMaxLength(100);
            entity.Property(e => e.FullName).HasMaxLength(100);
            entity.Property(e => e.IdentificationNumber).HasMaxLength(20);
            entity.Property(e => e.Phone).HasMaxLength(20);
        });

        modelBuilder.Entity<Permission>(entity =>
        {
            entity.HasKey(e => e.PermissionId).HasName("PK__Permissi__EFA6FB2FC9F3658D");

            entity.HasIndex(e => e.PermissionName, "UQ__Permissi__0FFDA3570B86F174").IsUnique();

            entity.Property(e => e.Description).HasMaxLength(255);
            entity.Property(e => e.PermissionName).HasMaxLength(100);
        });

        modelBuilder.Entity<Role>(entity =>
        {
            entity.HasKey(e => e.RoleId).HasName("PK__Roles__8AFACE1AD658464D");

            entity.HasIndex(e => e.RoleName, "UQ__Roles__8A2B61605B817779").IsUnique();

            entity.Property(e => e.Description).HasMaxLength(255);
            entity.Property(e => e.RoleName).HasMaxLength(50);
        });

        modelBuilder.Entity<RolePermission>(entity =>
        {
            entity.HasKey(e => e.RolePermissionId).HasName("PK__RolePerm__120F46BAAC837F24");

            entity.HasOne(d => d.Permission).WithMany(p => p.RolePermissions)
                .HasForeignKey(d => d.PermissionId)
                .HasConstraintName("FK__RolePermi__Permi__1DB06A4F");

            entity.HasOne(d => d.Role).WithMany(p => p.RolePermissions)
                .HasForeignKey(d => d.RoleId)
                .HasConstraintName("FK__RolePermi__RoleI__1CBC4616");
        });

        modelBuilder.Entity<Specialty>(entity =>
        {
            entity.HasKey(e => e.SpecialtyId).HasName("PK__Specialt__D768F6A878A0B57C");

            entity.Property(e => e.SpecialtyName).HasMaxLength(100);
        });

        modelBuilder.Entity<Token>(entity =>
        {
            entity.HasKey(e => e.TokenId).HasName("PK__Tokens__658FEEEACFB0756D");

            entity.Property(e => e.CreatedAt)
                .HasDefaultValueSql("(getdate())")
                .HasColumnType("datetime");
            entity.Property(e => e.ExpirationDate).HasColumnType("datetime");
            entity.Property(e => e.IsRevoked).HasDefaultValue(false);
            entity.Property(e => e.RevokedAt).HasColumnType("datetime");

            entity.HasOne(d => d.User).WithMany(p => p.Tokens)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("FK__Tokens__UserId__208CD6FA");
        });

        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.UserId).HasName("PK__Users__1788CC4C99067823");

            entity.HasIndex(e => e.Email, "UQ__Users__A9D10534268438A8").IsUnique();

            entity.Property(e => e.Email).HasMaxLength(100);
            entity.Property(e => e.FullName).HasMaxLength(100);
            entity.Property(e => e.IsActive).HasDefaultValue(true);
            entity.Property(e => e.Password).HasMaxLength(100);
            entity.Property(e => e.RegistrationDate)
                .HasDefaultValueSql("(getdate())")
                .HasColumnType("datetime");
            entity.Property(e => e.Role).HasMaxLength(50);
            entity.Property(e => e.UserName).HasMaxLength(100);
        });

        modelBuilder.Entity<UserRole>(entity =>
        {
            entity.HasKey(e => e.UserRoleId).HasName("PK__UserRole__3D978A3589EEE41D");

            entity.HasOne(d => d.Role).WithMany(p => p.UserRoles)
                .HasForeignKey(d => d.RoleId)
                .HasConstraintName("FK__UserRoles__RoleI__17036CC0");

            entity.HasOne(d => d.User).WithMany(p => p.UserRoles)
                .HasForeignKey(d => d.UserId)
                .HasConstraintName("FK__UserRoles__UserI__160F4887");
        });

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
