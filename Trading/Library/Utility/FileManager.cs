using cAlgo.API;
using cAlgo.API.Internals;

namespace AlgorithmicTrading.Utility
{
    internal static class FileManager
    {
        private static string BuildAlgoDirectoryPath(string fileSystem, string directoryName)
        {
            return $"{Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)}\\cAlgo\\{fileSystem}\\{directoryName}";
        }
        
        private static string BuildRobotFileName(string fileSystem, Symbol symbol, TimeFrame timeFrame, string fileName, string extension)
        {
            var directoryName = $"{symbol.Name.Replace("/", "")}\\{timeFrame.Name.Replace("/", "")}";
            return $"{BuildAlgoDirectoryPath(fileSystem, directoryName)}\\{fileName.Replace(" ", "")}{extension}";
        }
        
        internal static string BuildRecordFileName(Symbol symbol, TimeFrame timeFrame, string fileName)
        {
            return BuildRobotFileName(".records", symbol, timeFrame, fileName, ".temp");
        }
        
        internal static string BuildOptimizationFileName(Symbol symbol, TimeFrame timeFrame, string fileName)
        {
            return BuildRobotFileName("Optimizations", symbol, timeFrame, fileName, ".pdf");
        }
        
        internal static void CreateDirectory(string filePath) { Directory.CreateDirectory(Path.GetDirectoryName(filePath) ?? string.Empty); }
        
        internal static void SaveStringToFile(string filePath, string content)
        {
            CreateDirectory(filePath);
            using(var sw = File.CreateText(filePath))
                sw.WriteLine(content);
        }

        internal static string? LoadStringFromFile(string filePath)
        {
            if (!File.Exists(filePath))
                return null;
            using(var sw = File.OpenText(filePath))
                return sw.ReadLine();
        }
    }
}