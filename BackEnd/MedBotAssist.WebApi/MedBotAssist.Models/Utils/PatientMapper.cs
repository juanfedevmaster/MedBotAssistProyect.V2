using MedBotAssist.Models.DTOs;
using MedBotAssist.Models.Models;
using System;
using System.Collections.Generic;
using System.Linq;

namespace MedBotAssist.Models.Utils
{
    public static class PatientMapper
    {
        public static PatientInfoResponseDto ToInfoResponseDto(Patient patient)
        {
            return new PatientInfoResponseDto
            {
                PatientId = patient.PatientId.ToString(),
                Name = patient.FullName ?? string.Empty,
                IdentificationNumber = patient.IdentificationNumber ?? string.Empty,
                DateOfBirth = patient.BirthDate.HasValue ? patient.BirthDate.Value.ToDateTime(TimeOnly.MinValue) : DateTime.MinValue,
                Age = patient.BirthDate.HasValue ? DateTime.Now.Year - patient.BirthDate.Value.Year : 0,
                PhoneNumber = patient.Phone ?? string.Empty,
                Email = patient.Email ?? string.Empty
            };
        }

        public static Patient ToPatient(PatientInfoResponseDto dto)
        {
            return new Patient
            {
                PatientId = int.TryParse(dto.PatientId, out var id) ? id : 0,
                FullName = dto.Name,
                IdentificationNumber = dto.IdentificationNumber,
                BirthDate = dto.DateOfBirth != DateTime.MinValue ? DateOnly.FromDateTime(dto.DateOfBirth) : null,
                Phone = dto.PhoneNumber,
                Email = dto.Email
            };
        }

        public static PatientDetailedInfoResponseDto ToDetailedInfoResponseDto(
            Patient patient,
            IEnumerable<ClinicalSummary> clinicalSummaries)
        {
            return new PatientDetailedInfoResponseDto
            {
                PatientId = patient.PatientId.ToString(),
                Name = patient.FullName ?? string.Empty,
                IdentificationNumber = patient.IdentificationNumber ?? string.Empty,
                DateOfBirth = patient.BirthDate?.ToDateTime(TimeOnly.MinValue) ?? DateTime.MinValue,
                Age = patient.BirthDate.HasValue ? CalculateAge(patient.BirthDate.Value) : 0,
                PhoneNumber = patient.Phone ?? string.Empty,
                Email = patient.Email ?? string.Empty,
                ClinicalSummaries = clinicalSummaries.Select(cs => new ClinicalSummaryResponseDto
                {
                    SummaryId = cs.SummaryId,
                    Diagnosis = cs.Diagnosis,
                    Treatment = cs.Treatment,
                    Recommendations = cs.Recommendations,
                    NextSteps = cs.NextSteps,
                    GeneratedDate = cs.GeneratedDate,
                    MedicalNote = cs.Note == null ? null : new MedicalNoteResponseDto
                    {
                        NoteId = cs.Note.NoteId,
                        CreationDate = cs.Note.CreationDate,
                        FreeText = cs.Note.FreeText,
                        AppointmentId = cs.Note.AppointmentId
                    }
                }).ToList()
            };
        }

        private static int CalculateAge(DateOnly birthDate)
        {
            var today = DateOnly.FromDateTime(DateTime.Today);
            int age = today.Year - birthDate.Year;
            if (birthDate > today.AddYears(-age)) age--;
            return age;
        }
    }
}
