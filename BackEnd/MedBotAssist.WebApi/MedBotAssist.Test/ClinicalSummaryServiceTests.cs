using Xunit;
using System.Threading.Tasks;
using MedBotAssist.Models.Models;
using MedBotAssist.Persistance.Context;
using MedBotAssist.WebApi.Services.ClinicalSummaryService;
using Microsoft.EntityFrameworkCore;
using System;
using System.Linq;

namespace MedBotAssist.Test
{
    public class ClinicalSummaryServiceTests
    {
        private ClinicalSummaryService CreateService(string dbName)
        {
            var options = new DbContextOptionsBuilder<MedBotAssistDbContext>()
                .UseInMemoryDatabase(databaseName: dbName)
                .Options;
            var context = new MedBotAssistDbContext(options);
            return new ClinicalSummaryService(context);
        }

        [Fact]
        public async Task CreateAsync_AddsClinicalSummary()
        {
            var service = CreateService(nameof(CreateAsync_AddsClinicalSummary));
            var summary = new ClinicalSummary
            {
                Diagnosis = "Diagnóstico",
                Treatment = "Tratamiento",
                Recommendations = "Recomendaciones",
                NextSteps = "Pasos",
                GeneratedDate = DateTime.UtcNow
            };

            var result = await service.CreateAsync(summary);

            Assert.NotNull(result);
            Assert.Equal("Diagnóstico", result.Diagnosis);
            Assert.Single(service.GetAllAsync().Result);
        }

        [Fact]
        public async Task GetByIdAsync_ReturnsCorrectSummary()
        {
            var service = CreateService(nameof(GetByIdAsync_ReturnsCorrectSummary));
            var summary = new ClinicalSummary { Diagnosis = "D1" };
            await service.CreateAsync(summary);

            var result = await service.GetByIdAsync(summary.SummaryId);

            Assert.NotNull(result);
            Assert.Equal("D1", result.Diagnosis);
        }

        [Fact]
        public async Task GetAllAsync_ReturnsAllSummaries()
        {
            var service = CreateService(nameof(GetAllAsync_ReturnsAllSummaries));
            await service.CreateAsync(new ClinicalSummary { Diagnosis = "D1" });
            await service.CreateAsync(new ClinicalSummary { Diagnosis = "D2" });

            var result = await service.GetAllAsync();

            Assert.Equal(2, result.Count());
        }

        [Fact]
        public async Task UpdateAsync_UpdatesSummary()
        {
            var service = CreateService(nameof(UpdateAsync_UpdatesSummary));
            var summary = new ClinicalSummary { Diagnosis = "Old" };
            await service.CreateAsync(summary);

            summary.Diagnosis = "New";
            var updated = await service.UpdateAsync(summary);

            Assert.NotNull(updated);
            Assert.Equal("New", updated.Diagnosis);
        }

        [Fact]
        public async Task DeleteAsync_RemovesSummary()
        {
            var service = CreateService(nameof(DeleteAsync_RemovesSummary));
            var summary = new ClinicalSummary { Diagnosis = "D" };
            await service.CreateAsync(summary);

            var deleted = await service.DeleteAsync(summary.SummaryId);

            Assert.True(deleted);
            Assert.Empty(await service.GetAllAsync());
        }
    }
}
