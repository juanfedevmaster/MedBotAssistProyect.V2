using Xunit;
using Moq;
using System.Threading.Tasks;
using System.Collections.Generic;
using MedBotAssist.Interfaces;
using MedBotAssist.Models.Models;

namespace MedBotAssist.Test
{
    public class PatientServiceTests
    {
        private readonly Mock<IPatientService> _mockService;
        private readonly Patient _testPatient;

        public PatientServiceTests()
        {
            _mockService = new Mock<IPatientService>();
            _testPatient = new Patient
            {
                PatientId = 1,
                FullName = "John Doe",
                IdentificationNumber = "123456789",
                BirthDate = new DateOnly(1990, 1, 1),
                Phone = "555-1234",
                Email = "john@example.com"
            };
        }

        [Fact]
        public async Task CreateAsync_ShouldReturnCreatedPatient()
        {
            _mockService.Setup(s => s.CreateAsync(It.IsAny<Patient>()))
                        .ReturnsAsync(_testPatient);

            var result = await _mockService.Object.CreateAsync(_testPatient);

            Assert.NotNull(result);
            Assert.Equal(_testPatient.PatientId, result.PatientId);
        }

        [Fact]
        public async Task GetByIdAsync_ShouldReturnPatient_WhenExists()
        {
            _mockService.Setup(s => s.GetByIdAsync(1))
                        .ReturnsAsync(_testPatient);

            var result = await _mockService.Object.GetByIdAsync(1);

            Assert.NotNull(result);
            Assert.Equal("John Doe", result?.FullName);
        }

        [Fact]
        public async Task GetAllAsync_ShouldReturnPatients()
        {
            var patients = new List<Patient> { _testPatient };
            _mockService.Setup(s => s.GetAllAsync())
                        .ReturnsAsync(patients);

            var result = await _mockService.Object.GetAllAsync();

            Assert.NotEmpty(result);
        }

        [Fact]
        public async Task UpdateAsync_ShouldReturnUpdatedPatient()
        {
            var updatedPatient = _testPatient;
            updatedPatient.FullName = "Jane Doe";
            _mockService.Setup(s => s.UpdateAsync(It.IsAny<Patient>()))
                        .ReturnsAsync(updatedPatient);

            var result = await _mockService.Object.UpdateAsync(updatedPatient);

            Assert.Equal("Jane Doe", result?.FullName);
        }

        [Fact]
        public async Task DeleteAsync_ShouldReturnTrue_WhenDeleted()
        {
            _mockService.Setup(s => s.DeleteAsync(1))
                        .ReturnsAsync(true);

            var result = await _mockService.Object.DeleteAsync(1);

            Assert.True(result);
        }
    }
}
