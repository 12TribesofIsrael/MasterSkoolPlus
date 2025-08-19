#!/usr/bin/env python3
"""
Performance Benchmarks for Skool Scraper
========================================

Comprehensive performance testing and benchmarking for all components
of the scraping system. Measures execution time, memory usage, and
identifies performance bottlenecks.
"""

import sys
import os
import time
import json
import statistics
from unittest.mock import Mock, patch
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import psutil, fallback to simple memory tracking
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available, using simple memory tracking")

@dataclass
class BenchmarkResult:
    """Result of a performance benchmark"""
    operation: str
    duration: float
    memory_usage: float
    iterations: int
    avg_duration: float
    min_duration: float
    max_duration: float
    std_deviation: float
    success_rate: float
    details: Dict[str, Any]

class PerformanceBenchmark:
    """Performance benchmarking system"""
    
    def __init__(self):
        self.results = []
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()
        else:
            self.process = None
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if PSUTIL_AVAILABLE and self.process:
            return self.process.memory_info().rss / 1024 / 1024
        else:
            # Simple fallback - return 0 for memory tracking
            return 0.0
    
    @contextmanager
    def measure_performance(self, operation: str):
        """Context manager for measuring performance"""
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        try:
            yield
            success = True
        except Exception as e:
            success = False
            raise e
        finally:
            end_time = time.time()
            end_memory = self.get_memory_usage()
            
            duration = end_time - start_time
            memory_usage = end_memory - start_memory
            
            result = BenchmarkResult(
                operation=operation,
                duration=duration,
                memory_usage=memory_usage,
                iterations=1,
                avg_duration=duration,
                min_duration=duration,
                max_duration=duration,
                std_deviation=0.0,
                success_rate=1.0 if success else 0.0,
                details={}
            )
            self.results.append(result)
    
    def benchmark_function(self, func, operation: str, iterations: int = 10, 
                          *args, **kwargs) -> BenchmarkResult:
        """Benchmark a function with multiple iterations"""
        
        durations = []
        memory_usage = []
        successes = 0
        
        for i in range(iterations):
            start_time = time.time()
            start_memory = self.get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
                success = True
                successes += 1
            except Exception as e:
                success = False
                result = None
            
            end_time = time.time()
            end_memory = self.get_memory_usage()
            
            duration = end_time - start_time
            memory = end_memory - start_memory
            
            durations.append(duration)
            memory_usage.append(memory)
        
        # Calculate statistics
        avg_duration = statistics.mean(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        std_deviation = statistics.stdev(durations) if len(durations) > 1 else 0.0
        avg_memory = statistics.mean(memory_usage)
        success_rate = successes / iterations
        
        result = BenchmarkResult(
            operation=operation,
            duration=avg_duration,
            memory_usage=avg_memory,
            iterations=iterations,
            avg_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            std_deviation=std_deviation,
            success_rate=success_rate,
            details={
                "all_durations": durations,
                "all_memory": memory_usage,
                "successes": successes
            }
        )
        
        self.results.append(result)
        return result
    
    def print_results(self):
        """Print benchmark results in a formatted way"""
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE BENCHMARK RESULTS")
        print("=" * 80)
        
        for result in self.results:
            print(f"\n🔍 {result.operation}")
            print(f"   ⏱️  Average Duration: {result.avg_duration:.4f}s")
            print(f"   📈 Min/Max Duration: {result.min_duration:.4f}s / {result.max_duration:.4f}s")
            print(f"   📊 Standard Deviation: {result.std_deviation:.4f}s")
            if PSUTIL_AVAILABLE:
                print(f"   💾 Memory Usage: {result.memory_usage:.2f} MB")
            else:
                print(f"   💾 Memory Usage: {result.memory_usage:.2f} MB (estimated)")
            print(f"   ✅ Success Rate: {result.success_rate:.1%}")
            print(f"   🔄 Iterations: {result.iterations}")
    
    def export_results(self, filename: str = "benchmark_results.json"):
        """Export results to JSON file"""
        data = []
        for result in self.results:
            data.append({
                "operation": result.operation,
                "avg_duration": result.avg_duration,
                "min_duration": result.min_duration,
                "max_duration": result.max_duration,
                "std_deviation": result.std_deviation,
                "memory_usage": result.memory_usage,
                "success_rate": result.success_rate,
                "iterations": result.iterations,
                "details": result.details
            })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📁 Results exported to {filename}")

def benchmark_config_manager():
    """Benchmark configuration manager operations"""
    
    print("🧪 BENCHMARKING CONFIGURATION MANAGER")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Import config manager
    from skool_modules.config_manager import get_config, set_config
    
    # Benchmark config loading
    def test_config_loading():
        return get_config('SKOOL_BASE_URL')
    
    result = benchmark.benchmark_function(test_config_loading, "Config Loading", 100)
    print(f"✅ Config loading: {result.avg_duration:.6f}s avg")
    
    # Benchmark config setting
    def test_config_setting():
        set_config('TEST_BENCHMARK', 'value')
        return get_config('TEST_BENCHMARK')
    
    result = benchmark.benchmark_function(test_config_setting, "Config Setting", 100)
    print(f"✅ Config setting: {result.avg_duration:.6f}s avg")
    
    return benchmark

def benchmark_logger():
    """Benchmark logging operations"""
    
    print("\n🧪 BENCHMARKING LOGGER")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Import logger
    from skool_modules.logger import get_logger, log_info, log_error
    
    logger = get_logger()
    
    # Benchmark basic logging
    def test_basic_logging():
        logger.info("Test log message")
    
    result = benchmark.benchmark_function(test_basic_logging, "Basic Logging", 100)
    print(f"✅ Basic logging: {result.avg_duration:.6f}s avg")
    
    # Benchmark convenience functions
    def test_convenience_logging():
        log_info("Test info message")
        log_error("Test error message")
    
    result = benchmark.benchmark_function(test_convenience_logging, "Convenience Logging", 100)
    print(f"✅ Convenience logging: {result.avg_duration:.6f}s avg")
    
    # Benchmark structured logging
    def test_structured_logging():
        data = {"test": "data", "number": 123}
        logger.log_dict(data, "info")
    
    result = benchmark.benchmark_function(test_structured_logging, "Structured Logging", 100)
    print(f"✅ Structured logging: {result.avg_duration:.6f}s avg")
    
    return benchmark

def benchmark_error_handler():
    """Benchmark error handling operations"""
    
    print("\n🧪 BENCHMARKING ERROR HANDLER")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Import error handler
    from skool_modules.error_handler import safe_execute, handle_error, NetworkError
    
    # Benchmark safe_execute with success
    def test_safe_execute_success():
        def success_function():
            return "success"
        return safe_execute(success_function)
    
    result = benchmark.benchmark_function(test_safe_execute_success, "Safe Execute Success", 100)
    print(f"✅ Safe execute success: {result.avg_duration:.6f}s avg")
    
    # Benchmark safe_execute with error
    def test_safe_execute_error():
        def error_function():
            raise NetworkError("Test error")
        return safe_execute(error_function)
    
    result = benchmark.benchmark_function(test_safe_execute_error, "Safe Execute Error", 100)
    print(f"✅ Safe execute error: {result.avg_duration:.6f}s avg")
    
    # Benchmark direct error handling
    def test_direct_error_handling():
        try:
            raise NetworkError("Test error")
        except Exception as e:
            return handle_error(e, {"test": True})
    
    result = benchmark.benchmark_function(test_direct_error_handling, "Direct Error Handling", 100)
    print(f"✅ Direct error handling: {result.avg_duration:.6f}s avg")
    
    return benchmark

def benchmark_video_extractor():
    """Benchmark video extraction operations"""
    
    print("\n🧪 BENCHMARKING VIDEO EXTRACTOR")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Import video extractor
    from skool_modules.video_extractor import get_video_extractor, extract_video_url
    
    # Create mock driver
    from test_selenium_mocks import create_mock_driver_with_video_data
    
    # Benchmark video extractor initialization
    def test_extractor_init():
        return get_video_extractor()
    
    result = benchmark.benchmark_function(test_extractor_init, "Video Extractor Init", 50)
    print(f"✅ Extractor initialization: {result.avg_duration:.6f}s avg")
    
    # Benchmark video extraction with mock data
    def test_video_extraction():
        driver = create_mock_driver_with_video_data("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        return extract_video_url(driver, "Test Lesson")
    
    result = benchmark.benchmark_function(test_video_extraction, "Video Extraction", 100)
    print(f"✅ Video extraction: {result.avg_duration:.6f}s avg")
    
    # Benchmark statistics retrieval
    def test_statistics_retrieval():
        extractor = get_video_extractor()
        return extractor.get_extraction_statistics()
    
    result = benchmark.benchmark_function(test_statistics_retrieval, "Statistics Retrieval", 100)
    print(f"✅ Statistics retrieval: {result.avg_duration:.6f}s avg")
    
    return benchmark

def benchmark_browser_manager():
    """Benchmark browser manager operations"""
    
    print("\n🧪 BENCHMARKING BROWSER MANAGER")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Import browser manager
    from skool_modules.browser_manager import should_use_browser_isolation
    
    # Benchmark isolation decision logic
    def test_isolation_decision():
        return should_use_browser_isolation("Test Lesson", 5, 10)
    
    result = benchmark.benchmark_function(test_isolation_decision, "Isolation Decision", 1000)
    print(f"✅ Isolation decision: {result.avg_duration:.6f}s avg")
    
    # Benchmark multiple isolation decisions
    def test_multiple_isolation_decisions():
        results = []
        for i in range(1, 11):
            results.append(should_use_browser_isolation(f"Lesson {i}", i, 10))
        return results
    
    result = benchmark.benchmark_function(test_multiple_isolation_decisions, "Multiple Isolation Decisions", 100)
    print(f"✅ Multiple isolation decisions: {result.avg_duration:.6f}s avg")
    
    return benchmark

def benchmark_mock_objects():
    """Benchmark mock object operations"""
    
    print("\n🧪 BENCHMARKING MOCK OBJECTS")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Import mock objects
    from test_selenium_mocks import MockWebDriver, MockWebElement, create_mock_driver_with_video_data
    
    # Benchmark mock driver creation
    def test_mock_driver_creation():
        return MockWebDriver()
    
    result = benchmark.benchmark_function(test_mock_driver_creation, "Mock Driver Creation", 1000)
    print(f"✅ Mock driver creation: {result.avg_duration:.6f}s avg")
    
    # Benchmark mock element creation
    def test_mock_element_creation():
        return MockWebElement("div", "Test text", {"id": "test"})
    
    result = benchmark.benchmark_function(test_mock_element_creation, "Mock Element Creation", 1000)
    print(f"✅ Mock element creation: {result.avg_duration:.6f}s avg")
    
    # Benchmark mock driver with video data
    def test_mock_driver_with_video():
        return create_mock_driver_with_video_data("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    result = benchmark.benchmark_function(test_mock_driver_with_video, "Mock Driver with Video Data", 100)
    print(f"✅ Mock driver with video data: {result.avg_duration:.6f}s avg")
    
    # Benchmark element finding
    def test_element_finding():
        driver = MockWebDriver()
        driver.add_element("test", MockWebElement("div", "Test"))
        return driver.find_element("id", "test")
    
    result = benchmark.benchmark_function(test_element_finding, "Element Finding", 1000)
    print(f"✅ Element finding: {result.avg_duration:.6f}s avg")
    
    return benchmark

def benchmark_integration_workflow():
    """Benchmark complete integration workflow"""
    
    print("\n🧪 BENCHMARKING INTEGRATION WORKFLOW")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Import all modules
    from skool_modules.config_manager import get_config
    from skool_modules.logger import get_logger
    from skool_modules.error_handler import safe_execute
    from skool_modules.video_extractor import extract_video_url
    from test_selenium_mocks import create_mock_driver_with_video_data
    
    # Benchmark complete lesson extraction workflow
    def test_complete_lesson_workflow():
        # Step 1: Configuration
        base_url = get_config('SKOOL_BASE_URL')
        
        # Step 2: Logger
        logger = get_logger()
        logger.info("Starting lesson extraction")
        
        # Step 3: Create mock driver
        driver = create_mock_driver_with_video_data("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        # Step 4: Extract video
        video_url = extract_video_url(driver, "Test Lesson")
        
        # Step 5: Log results
        logger.success(f"Extracted video: {video_url}")
        
        return video_url
    
    result = benchmark.benchmark_function(test_complete_lesson_workflow, "Complete Lesson Workflow", 50)
    print(f"✅ Complete lesson workflow: {result.avg_duration:.6f}s avg")
    
    # Benchmark community extraction workflow
    def test_community_workflow():
        logger = get_logger()
        logger.info("Starting community extraction")
        
        lessons = []
        for i in range(5):
            driver = create_mock_driver_with_video_data(f"https://www.youtube.com/watch?v=video{i}")
            video_url = extract_video_url(driver, f"Lesson {i+1}")
            lessons.append({"title": f"Lesson {i+1}", "video": video_url})
        
        logger.success(f"Extracted {len(lessons)} lessons")
        return lessons
    
    result = benchmark.benchmark_function(test_community_workflow, "Community Workflow", 20)
    print(f"✅ Community workflow: {result.avg_duration:.6f}s avg")
    
    return benchmark

def benchmark_memory_usage():
    """Benchmark memory usage patterns"""
    
    print("\n🧪 BENCHMARKING MEMORY USAGE")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Import modules
    from skool_modules.logger import get_logger
    from skool_modules.video_extractor import get_video_extractor
    from test_selenium_mocks import MockWebDriver, MockWebElement
    
    # Benchmark logger memory usage
    def test_logger_memory():
        logger = get_logger()
        for i in range(100):
            logger.info(f"Log message {i}")
        return True
    
    result = benchmark.benchmark_function(test_logger_memory, "Logger Memory Usage", 10)
    print(f"✅ Logger memory usage: {result.memory_usage:.2f} MB avg")
    
    # Benchmark video extractor memory usage
    def test_video_extractor_memory():
        extractor = get_video_extractor()
        for i in range(50):
            driver = MockWebDriver()
            extract_video_url(driver, f"Lesson {i}")
        return True
    
    result = benchmark.benchmark_function(test_video_extractor_memory, "Video Extractor Memory Usage", 10)
    print(f"✅ Video extractor memory usage: {result.memory_usage:.2f} MB avg")
    
    # Benchmark mock objects memory usage
    def test_mock_objects_memory():
        drivers = []
        for i in range(100):
            driver = MockWebDriver()
            for j in range(10):
                driver.add_element(f"element_{j}", MockWebElement("div", f"Text {j}"))
            drivers.append(driver)
        return len(drivers)
    
    result = benchmark.benchmark_function(test_mock_objects_memory, "Mock Objects Memory Usage", 5)
    print(f"✅ Mock objects memory usage: {result.memory_usage:.2f} MB avg")
    
    return benchmark

def benchmark_concurrent_operations():
    """Benchmark concurrent operations"""
    
    print("\n🧪 BENCHMARKING CONCURRENT OPERATIONS")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    import threading
    from skool_modules.logger import get_logger
    from skool_modules.video_extractor import get_video_extractor
    from test_selenium_mocks import create_mock_driver_with_video_data
    
    # Benchmark concurrent logging
    def test_concurrent_logging():
        logger = get_logger()
        
        def log_worker(worker_id):
            for i in range(10):
                logger.info(f"Worker {worker_id} - Message {i}")
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        return True
    
    result = benchmark.benchmark_function(test_concurrent_logging, "Concurrent Logging", 10)
    print(f"✅ Concurrent logging: {result.avg_duration:.6f}s avg")
    
    # Benchmark concurrent video extraction
    def test_concurrent_video_extraction():
        extractor = get_video_extractor()
        
        def extraction_worker(worker_id):
            for i in range(5):
                driver = create_mock_driver_with_video_data(f"https://www.youtube.com/watch?v=video{worker_id}_{i}")
                extract_video_url(driver, f"Lesson {worker_id}_{i}")
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=extraction_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        return True
    
    result = benchmark.benchmark_function(test_concurrent_video_extraction, "Concurrent Video Extraction", 10)
    print(f"✅ Concurrent video extraction: {result.avg_duration:.6f}s avg")
    
    return benchmark

def run_all_benchmarks():
    """Run all performance benchmarks"""
    
    print("🚀 Starting Performance Benchmarks")
    print("=" * 60)
    
    # Run all benchmarks
    benchmarks = [
        benchmark_config_manager,
        benchmark_logger,
        benchmark_error_handler,
        benchmark_video_extractor,
        benchmark_browser_manager,
        benchmark_mock_objects,
        benchmark_integration_workflow,
        benchmark_memory_usage,
        benchmark_concurrent_operations
    ]
    
    all_results = []
    
    for benchmark_func in benchmarks:
        try:
            benchmark = benchmark_func()
            all_results.extend(benchmark.results)
        except Exception as e:
            print(f"❌ Benchmark {benchmark_func.__name__} failed: {e}")
    
    # Create combined benchmark object
    combined_benchmark = PerformanceBenchmark()
    combined_benchmark.results = all_results
    
    # Print all results
    combined_benchmark.print_results()
    
    # Export results
    combined_benchmark.export_results()
    
    # Performance summary
    print("\n" + "=" * 80)
    print("📈 PERFORMANCE SUMMARY")
    print("=" * 80)
    
    # Find fastest and slowest operations
    if all_results:
        fastest = min(all_results, key=lambda x: x.avg_duration)
        slowest = max(all_results, key=lambda x: x.avg_duration)
        
        print(f"\n⚡ Fastest Operation: {fastest.operation} ({fastest.avg_duration:.6f}s)")
        print(f"🐌 Slowest Operation: {slowest.operation} ({slowest.avg_duration:.6f}s)")
        
        # Calculate total time
        total_time = sum(r.avg_duration for r in all_results)
        print(f"⏱️  Total Benchmark Time: {total_time:.4f}s")
        
        # Memory usage summary
        total_memory = sum(r.memory_usage for r in all_results)
        avg_memory = statistics.mean(r.memory_usage for r in all_results)
        print(f"💾 Total Memory Usage: {total_memory:.2f} MB")
        print(f"📊 Average Memory Usage: {avg_memory:.2f} MB")
        
        # Success rate summary
        avg_success_rate = statistics.mean(r.success_rate for r in all_results)
        print(f"✅ Average Success Rate: {avg_success_rate:.1%}")
    
    print("\n" + "=" * 80)
    print("🎯 BENCHMARK COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    run_all_benchmarks()
