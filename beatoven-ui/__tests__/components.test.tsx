/**
 * Component Tests
 */

import React from 'react';
import renderer from 'react-test-renderer';

// Mock react-native-svg
jest.mock('react-native-svg', () => ({
  Svg: 'Svg',
  Rect: 'Rect',
}));

describe('NodeCard', () => {
  it('renders without crashing', () => {
    const NodeCard = require('../src/components/NodeCard').default;
    const tree = renderer.create(
      <NodeCard
        name="Test Module"
        color="#00D9FF"
        inputs={['in1']}
        outputs={['out1']}
        isActive={false}
        onPress={() => {}}
      />
    );
    expect(tree).toBeTruthy();
  });

  it('renders active state', () => {
    const NodeCard = require('../src/components/NodeCard').default;
    const tree = renderer.create(
      <NodeCard
        name="Active Module"
        color="#FF6B6B"
        inputs={[]}
        outputs={['output']}
        isActive={true}
        onPress={() => {}}
      />
    );
    expect(tree).toBeTruthy();
  });
});

describe('SliderControl', () => {
  it('renders without crashing', () => {
    const SliderControl = require('../src/components/SliderControl').default;
    const tree = renderer.create(
      <SliderControl
        label="Test Slider"
        value={0.5}
        onValueChange={() => {}}
        valueDisplay="50%"
        color="#00D9FF"
      />
    );
    expect(tree).toBeTruthy();
  });

  it('renders disabled state', () => {
    const SliderControl = require('../src/components/SliderControl').default;
    const tree = renderer.create(
      <SliderControl
        label="Disabled"
        value={0.3}
        onValueChange={() => {}}
        disabled={true}
      />
    );
    expect(tree).toBeTruthy();
  });
});

describe('ToggleControl', () => {
  it('renders without crashing', () => {
    const ToggleControl = require('../src/components/ToggleControl').default;
    const tree = renderer.create(
      <ToggleControl
        label="Test Toggle"
        value={true}
        onValueChange={() => {}}
        description="A test toggle"
      />
    );
    expect(tree).toBeTruthy();
  });
});

describe('StemCard', () => {
  it('renders without crashing', () => {
    const StemCard = require('../src/components/StemCard').default;
    const mockWaveform = Array(50).fill(0).map(() => Math.random());
    const tree = renderer.create(
      <StemCard
        name="drums"
        duration={16.0}
        waveform={mockWaveform}
        color="#FF6B6B"
        isPlaying={false}
        onPlay={() => {}}
        onDownload={() => {}}
      />
    );
    expect(tree).toBeTruthy();
  });

  it('renders playing state', () => {
    const StemCard = require('../src/components/StemCard').default;
    const mockWaveform = Array(50).fill(0.5);
    const tree = renderer.create(
      <StemCard
        name="bass"
        duration={8.0}
        waveform={mockWaveform}
        color="#4ECDC4"
        isPlaying={true}
        onPlay={() => {}}
        onDownload={() => {}}
      />
    );
    expect(tree).toBeTruthy();
  });
});
